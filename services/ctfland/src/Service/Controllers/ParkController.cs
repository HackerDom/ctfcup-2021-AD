using System;
using System.Collections.Generic;
using System.Linq;
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

        public ParkController(DbContext dbContext, ILandingTemplateProvider landingTemplateProvider, TemplateRenderer templateRenderer)
        {
            this.dbContext = dbContext;
            this.landingTemplateProvider = landingTemplateProvider;
            this.templateRenderer = templateRenderer;
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

        [HttpGet]
        [Route("{parkId:guid}")]
        public async Task<IActionResult> Show(Guid parkId)
        {
            var park = await GetPark(parkId).ConfigureAwait(false);
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

        [HttpPost]
        [Route("create")]
        public async Task<IActionResult> Create(CreateParkRequestModel requestModel)
        {
            if (!ModelState.IsValid)
            {
               ModelState.AddModelError("", "Validation failed");
               return RedirectToAction("Create");
            }
            
            var user = await dbContext.Users.FindAsync(User.GetUserId()).ConfigureAwait(false);
            if (user is null)
                return RedirectToAction("Logout", "Auth");

            var parkWithSameName = await dbContext.Parks.FirstOrDefaultAsync(p => p.Name == requestModel.Name).ConfigureAwait(false);
            if (parkWithSameName is not null)
                return BadRequest("Park with same name is already added");

            var template = await landingTemplateProvider.GetLandingTemplate(requestModel).ConfigureAwait(false);
            if (template is null)
                return BadRequest("Something went wrong");

            var isValid = await landingTemplateProvider.IsTemplateValid(template, User.GetUserId())
                .ConfigureAwait(false);
            if (!isValid)
                return BadRequest("Something went wrong");

            var park = new Park
            {
                Id = Guid.NewGuid(),
                Contact = requestModel.Contact,
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

            return RedirectToAction("Show", new {parkId = park.Id});
        }

        [HttpGet]
        [Route("")]
        public IActionResult GetList([FromQuery] int skip = 0, [FromQuery] int take = 100)
        {
            var parks = GetParks(skip, take, true, false);
            var model = new ParksListViewModel { Parks = parks };
            return View(model);
        }

        [HttpGet]
        [Route("my")]
        public IActionResult MyParks(int skip = 0, int take = 100)
        {
            var parks = GetParks(skip, take, false, true);

            return View(new ParksListViewModel {Parks = parks});
        }

        [HttpPost]
        [Route("{id:guid}/delete")]
        public async Task<IActionResult> Delete(Guid id)
        {
            var park = await GetPark(id).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            dbContext.Parks.Remove(park);
            await dbContext.SaveChangesAsync().ConfigureAwait(false);

            return RedirectToAction("MyParks");
        }

        [HttpGet]
        [Route("{parkId:guid}/addAttraction")]
        public async Task<IActionResult> AddAttraction(Guid parkId)
        {
            var park = await GetPark(parkId).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            return View();
        }

        [HttpPost]
        [Route("{parkId:guid}/addAttraction")]
        public async Task<IActionResult> AddAttraction(Guid parkId, AddAttractionRequestModel model)
        {
            var park = await GetPark(parkId).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            var attraction = new Attraction
            {
                Cost = model.Cost,
                Name = model.Name,
                Description = model.Description,
            };

            await dbContext.Attractions.AddAsync(attraction).ConfigureAwait(false);
            park.Attractions.Add(attraction);

            await dbContext.SaveChangesAsync().ConfigureAwait(false);
            return RedirectToAction("MyParks");
        }

        private async Task<Park> GetPark(Guid id)
        {
            return await dbContext.Parks
                .AsQueryable()
                .Include(park => park.Owner)
                .Include(park => park.Attractions)
                .FirstOrDefaultAsync(park => park.Id == id)
                .ConfigureAwait(false);
        }


        private Park[] GetParks(int skip, int take, bool isPublicOnly, bool isOwnOnly)
        {
            var parks = dbContext.Parks
                .AsQueryable()
                .Include(park => park.Owner)
                .Include(park => park.Attractions)
                .AsEnumerable()
                .Where(park => !isOwnOnly || park.Owner.Id == User.GetUserId())
                .Where(park => !isPublicOnly || park.IsPublic)
                .OrderByDescending(park => park.CreatedAt)
                .Skip(skip)
                .Take(take)
                .ToArray();
            return parks;
        }
    }
}