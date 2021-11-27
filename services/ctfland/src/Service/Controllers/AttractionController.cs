using System;
using System.Threading.Tasks;
using CtfLand.DataLayer;
using CtfLand.DataLayer.Models;
using CtfLand.Service.Models;
using CtfLand.Service.Providers;
using Microsoft.AspNetCore.Mvc;


namespace CtfLand.Service.Controllers
{
    [Route("attraction")]
    public class AttractionController : Controller
    {
        private readonly DbContext dbContext;
        private readonly IParksProvider parksProvider;

        public AttractionController(DbContext dbContext, IParksProvider parksProvider)
        {
            this.dbContext = dbContext;
            this.parksProvider = parksProvider;
        }

        [HttpGet]
        [Route("{parkId:guid}/add")]
        public async Task<IActionResult> Add(Guid parkId)
        {
            var park = await parksProvider.GetPark(parkId).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            return View();
        }

        [HttpPost]
        [Route("{parkId:guid}/add")]
        public async Task<IActionResult> Add(Guid parkId, AddAttractionRequestModel model)
        {
            var park = await parksProvider.GetPark(parkId).ConfigureAwait(false);
            if (park is null)
                return NotFound();

            if (park.Owner.Id != User.GetUserId())
                return Forbid();

            var attraction = new Attraction
            {
                Cost = model.Cost,
                Name = model.Name,
                Description = model.Description,
                TicketKey = model.TicketKey,
            };

            await dbContext.Attractions.AddAsync(attraction).ConfigureAwait(false);
            park.Attractions.Add(attraction);

            await dbContext.SaveChangesAsync().ConfigureAwait(false);
            return RedirectToAction("MyParks", "Park");
        }
    }
}