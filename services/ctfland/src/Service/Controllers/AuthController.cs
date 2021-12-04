using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using CtfLand.DataLayer.Models;
using CtfLand.Service.Models;
using CtfLand.Service.Providers;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DbContext = CtfLand.DataLayer.DbContext;

namespace CtfLand.Service.Controllers
{
    [Route("auth")]
    public class AuthController : Controller
    {
        private readonly DbContext db;
        private readonly HashPasswordProvider hashPasswordProvider;

        public AuthController(DbContext db, HashPasswordProvider hashPasswordProvider)
        {
            this.db = db;
            this.hashPasswordProvider = hashPasswordProvider;
        }

        [HttpGet]
        [Route("login")]
        public IActionResult Login(string returnUrl = null)
        {
            return View(new LoginRequestModel {ReturnUrl = returnUrl});
        }

        [HttpPost]
        [Route("login")]
        public async Task<IActionResult> Login(LoginRequestModel model, [FromQuery] string returnUrl = null)
        {
            if (!ModelState.IsValid)
            {
                ModelState.AddModelError("", "Не указаны логин или пароль!");
                return Login();
            }

            var user = await db.Users.FirstOrDefaultAsync(user => user.Login == model.Login)
                .ConfigureAwait(false);
            if (user == null || !hashPasswordProvider.IsPasswordCorrect(model.Password, user.Salt, user.PasswordHash))
            {
                ModelState.AddModelError("", "Некорректные логин и(или) пароль");
                return Login();
            }

            await Authenticate(user).ConfigureAwait(false);
            return Redirect(returnUrl ?? "/");
        }

        [HttpGet]
        [Route("register")]
        public IActionResult Register()
        {
            return View();
        }

        [HttpPost]
        [Route("register")]
        public async Task<IActionResult> Register(RegisterRequestModel model)
        {
            if (!ModelState.IsValid)
            {
                ModelState.AddModelError("", "Заполнены не все обязательные поля");
                return Register();
            }

            var user = await AddUser(model).ConfigureAwait(false);
            if (user != null)
                return RedirectToAction("Index", "Home");

            return BadRequest("User with same login has already been added");
        }

        [HttpPost]
        [Authorize]
        [Route("logout")]
        public async Task<IActionResult> Logout(string returnUrl = null)
        {
            await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            return RedirectToAction("Index", "Home");
        }

        [HttpGet]
        [Route("forbidden")]
        public IActionResult Forbidden()
        {
            return View();
        }

        [HttpGet]
        [Authorize]
        [Route("profile/{id:guid}")]
        public async Task<IActionResult> Profile(Guid id)
        {
            var user = await db.Users.FindAsync(id).ConfigureAwait(false);
            var userBalance =  await db.UserBalances.FindAsync(id).ConfigureAwait(false);

            var userPurchases = await GetPurchasesViewModel(user).ConfigureAwait(false);
            var model = new ProfileViewModel
            {
                User = user, 
                CurrentBalance = userBalance.Balance,
                Purchases = userPurchases,
            };
            return View(model);
        }

        private async Task<ICollection<PurchaseViewModel>> GetPurchasesViewModel(User user)
        {
            var names = await db.UserPurchases
                .AsQueryable()
                .Where(purchase => purchase.UserId == user.Id)
                .Select(purchase => purchase.Name)
                .ToListAsync()
                .ConfigureAwait(false);

            var attractions = await db.Attractions
                .AsQueryable()
                .Where(attraction => names.Contains(attraction.Name))
                .ToListAsync()
                .ConfigureAwait(false);

            return attractions
                .Select(attraction => new PurchaseViewModel
                    {
                        AttractionName = attraction.Name,
                        TicketKey = attraction.TicketKey,
                    })
                .ToList();
        }

        private async Task<User> AddUser(RegisterRequestModel model)
        {
            var userWithSameLogin = await db.Users
                .FirstOrDefaultAsync(user => user.Login == model.Login)
                .ConfigureAwait(false);
            if (userWithSameLogin != null)
                return null;

            var (hash, salt) = hashPasswordProvider.GetPasswordHash(model.Password);
            var user = new User
            {
                Login = model.Login,
                PasswordHash = hash,
                Salt = salt,
                Document = model.Document,
                RegisteredAt = DateTime.UtcNow,
            };
            var entityEntry = await db.Users.AddAsync(user).ConfigureAwait(false);

            var userBalance = new UserBalance { Balance = 1000, UserId = entityEntry.Entity.Id };
            await db.UserBalances.AddAsync(userBalance).ConfigureAwait(false);
            
            await db.SaveChangesAsync().ConfigureAwait(false);
            return entityEntry.Entity;
        }

        private async Task Authenticate(User user)
        {
            var claims = new List<Claim>
            {
                new(ClaimTypes.Name, user.Login),
                new(ClaimTypes.Sid, user.Id.ToString()),
            };
            var identity = new ClaimsIdentity(claims,
                "ApplicationCookie",
                ClaimsIdentity.DefaultNameClaimType,
                ClaimsIdentity.DefaultRoleClaimType);
            await HttpContext.SignInAsync(
                    CookieAuthenticationDefaults.AuthenticationScheme, 
                    new ClaimsPrincipal(identity))
                .ConfigureAwait(false);
        }
    }
}