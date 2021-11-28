using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using CtfLand.DataLayer.Models;
using CtfLand.Service.Models;
using CtfLand.Service.Providers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DbContext = CtfLand.DataLayer.DbContext;

namespace CtfLand.Service.Controllers
{
    [Route("park")]
    [Authorize]
    public class ParkController : Controller
    {
        private readonly DbContext dbContext;
        private readonly ILandingTemplateProvider landingTemplateProvider;
        private readonly TemplateRenderer templateRenderer;
        private readonly IParksProvider parksProvider;

        public ParkController(
            DbContext dbContext,
            ILandingTemplateProvider landingTemplateProvider,
            TemplateRenderer templateRenderer,
            IParksProvider parksProvider)
        {
            this.dbContext = dbContext;
            this.landingTemplateProvider = landingTemplateProvider;
            this.templateRenderer = templateRenderer;
            this.parksProvider = parksProvider;
        }

        [HttpGet]
        [Route("{parkId:guid}")]
        public async Task<IActionResult> Get(Guid parkId)
        {
            var park = await parksProvider.GetPark(parkId).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            var model = new ParkLandingTemplateViewModel
            {
                UserId = User.GetUserId(),
                Attractions = park.Attractions ?? new List<Attraction>(),
                ShowBuyButton = User.IsVisitor(),
            };
            var template = await templateRenderer.RenderTemplate(park.Template, model).ConfigureAwait(false);

            return Content(template, "text/html", Encoding.UTF8);
        }
        
        [HttpGet]
        [Route("create")]
        [Access(UserRole.Moderator)]
        public IActionResult Create()
        {
            return View(new CreateParkViewModel
            {
                AllowedAttractionVariables = landingTemplateProvider.GetAllowedAttractionVariables,
                AllowedDescVariables = landingTemplateProvider.GetAllowedDescVariables,
            });
        }

        [HttpPost]
        [Route("create")]
        [Access(UserRole.Moderator)]
        public async Task<IActionResult> Create(CreateParkRequestModel requestModel)
        {
            if (!ModelState.IsValid)
            {
               ModelState.AddModelError("", "Ошибка при создании парка");
               return Create();
            }
            
            var user = await dbContext.Users.FindAsync(User.GetUserId()).ConfigureAwait(false);
            if (user is null)
                return RedirectToAction("Logout", "Auth");

            var parkWithSameName = await dbContext.Parks.FirstOrDefaultAsync(p => p.Name == requestModel.Name).ConfigureAwait(false);
            if (parkWithSameName is not null)
            {
                ModelState.AddModelError("", "Парк с таким именем уже создан");
                return Create();
            }

            var template = await landingTemplateProvider.GetLandingTemplate(requestModel).ConfigureAwait(false);
            if (template is null)
            {
                ModelState.AddModelError("", "Ошибка при создании парка - перепроверьте описания парка и шаблон атракционов");
                return Create();
            }

            var isValid = await landingTemplateProvider.IsTemplateValid(template, User.GetUserId())
                .ConfigureAwait(false);
            if (!isValid)
            {
                ModelState.AddModelError("", "Ошибка при создании парка - перепроверьте описания парка и шаблон атракционов");
                return Create();
            }

            var park = new Park
            {
                Id = Guid.NewGuid(),
                Contact = requestModel.Email,
                Name = requestModel.Name,
                Description = requestModel.Description,
                MaxVisitorsCount = requestModel.MaxVisitorsCount,
                Owner = user,
                Template = template,
                CreatedAt = DateTime.UtcNow,
                IsPublic = requestModel.IsPublic,
            };
            await dbContext.Parks.AddAsync(park).ConfigureAwait(false);
            await dbContext.SaveChangesAsync().ConfigureAwait(false);

            return RedirectToAction("Get", new {parkId = park.Id});
        }

        [HttpGet]
        [Route("")]
        public IActionResult GetList([FromQuery] int skip = 0, [FromQuery] int take = 100)
        {
            var parks = parksProvider.GetParks(skip, take, true, null);
            var model = new ParksListViewModel { Parks = parks };
            return View(model);
        }

        [HttpGet]
        [Route("my")]
        [Access(UserRole.Moderator)]
        public IActionResult MyParks([FromQuery] int skip = 0, [FromQuery] int take = 100)
        {
            var parks = parksProvider.GetParks(skip, take, false, User.GetUserId());

            return View(new ParksListViewModel {Parks = parks});
        }

        [HttpPost]
        [Route("{id:guid}/delete")]
        [Access(UserRole.Moderator)]
        public async Task<IActionResult> Delete(Guid id)
        {
            var park = await parksProvider.GetPark(id).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();
            
            dbContext.Attractions.RemoveRange(park.Attractions);
            dbContext.Parks.Remove(park);
            await dbContext.SaveChangesAsync().ConfigureAwait(false);

            return RedirectToAction("MyParks");
        }

        [HttpPost]
        [Route("{id:guid}/change-visibility")]
        [Access(UserRole.Moderator)]
        public async Task<IActionResult> ChangeVisibility(Guid id)
        {
            var park = await parksProvider.GetPark(id).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            park.IsPublic = !park.IsPublic;
            dbContext.Update(park);
            await dbContext.SaveChangesAsync().ConfigureAwait(false);

            return RedirectToAction("MyParks");
        }
    }
}