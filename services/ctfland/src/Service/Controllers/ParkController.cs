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
            };
            var template = await templateRenderer.RenderTemplate(park.Template, model).ConfigureAwait(false);

            return Content(template, "text/html", Encoding.UTF8);
        }
        
        [HttpGet]
        [Route("create")]
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

            var park = await parksProvider.Create(requestModel, template, user).ConfigureAwait(false);

            return RedirectToAction("Get", new {parkId = park.Id});
        }

        [HttpGet]
        [Route("")]
        public async Task<IActionResult> GetList([FromQuery] int skip = 0, [FromQuery] int take = 100)
        {
            var filter = new ParksListFilter(true, null);
            
            var totalCount = await parksProvider.Count(filter).ConfigureAwait(false);
            var parks = await parksProvider.GetParks(skip, take, filter).ConfigureAwait(false);
            
            return View(new ParksListViewModel { Parks = parks, TotalCount = totalCount});
        }

        [HttpGet]
        [Route("my")]
        public async Task<IActionResult> MyParks([FromQuery] int skip = 0, [FromQuery] int take = 100)
        {
            var filter = new ParksListFilter(false, User.GetUserId());
            
            var totalCount = await parksProvider.Count(filter).ConfigureAwait(false);
            var parks = await parksProvider.GetParks(skip, take, filter).ConfigureAwait(false);

            return View(new ParksListViewModel {Parks = parks, TotalCount = totalCount});
        }

        [HttpPost]
        [Route("{id:guid}/delete")]
        public async Task<IActionResult> Delete(Guid id)
        {
            var park = await parksProvider.GetPark(id).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            await parksProvider.Remove(park).ConfigureAwait(false);

            return RedirectToAction("MyParks");
        }

        [HttpPost]
        [Route("{id:guid}/change-visibility")]
        public async Task<IActionResult> ChangeVisibility(Guid id)
        {
            var park = await parksProvider.GetPark(id).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            await parksProvider.ChangeVisibility(park).ConfigureAwait(false);

            return RedirectToAction("MyParks");
        }
    }
}