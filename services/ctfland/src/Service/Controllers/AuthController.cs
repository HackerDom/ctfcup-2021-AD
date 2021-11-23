using System;
using System.Collections.Generic;
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
        public IActionResult Login()
        {
            return View();
        }

        [HttpPost]
        [Route("login")]
        public async Task<IActionResult> Login(LoginRequestModel model, string returnUrl = null)
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
            return View(user);
        }

        private async Task<User> AddUser(RegisterRequestModel model)
        {
            var userWithSameLogin = await db.Users.FirstOrDefaultAsync(user => user.Login == model.Login).ConfigureAwait(false);
            if (userWithSameLogin != null)
                return null;

            var (hash, salt) = hashPasswordProvider.GetPasswordHash(model.Password);
            var user = new User
            {
                Login = model.Login,
                Role = model.Role,
                PasswordHash = hash,
                Salt = salt,
                Document = model.Document,
                RegisteredAt = DateTime.UtcNow,
            };
            var entityEntry = await db.Users.AddAsync(user).ConfigureAwait(false);
            await db.SaveChangesAsync().ConfigureAwait(false);
            return entityEntry.Entity;
        }

        private async Task Authenticate(User user)
        {
            var claims = new List<Claim>
            {
                new(ClaimTypes.Name, user.Login),
                new(ClaimTypes.Role, user.Role.ToString("G")),
                new(ClaimTypes.Sid, user.Id.ToString())
            };
            var identity = new ClaimsIdentity(claims,
                "ApplicationCookie",
                ClaimsIdentity.DefaultNameClaimType,
                ClaimsIdentity.DefaultRoleClaimType);
            await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(identity))
                .ConfigureAwait(false);
        }
    }
}