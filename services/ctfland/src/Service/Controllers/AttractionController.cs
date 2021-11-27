using System;
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
    [Authorize]
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
        [Access(UserRole.Moderator)]
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
        [Access(UserRole.Moderator)]
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

        [HttpPost]
        [Route("{attractionId:guid}/buy")]
        [Access(UserRole.Visitor)]
        public async Task<IActionResult> Buy(Guid attractionId)
        {
            if (!User.IsVisitor())
                return BadRequest($"{User.GetUserRole():G} can't buy tickets to attraction");

            var attraction = await dbContext.Attractions
                .AsQueryable()
                .Include(attraction => attraction.Park)
                .FirstOrDefaultAsync(attraction => attraction.Id == attractionId)
                .ConfigureAwait(false);
            if (attraction is null)
                return NotFound();

            var userId = User.GetUserId();
            
            await using var transaction = await dbContext.Database.BeginTransactionAsync();
            var userBalance = await dbContext.UserBalances.FindAsync(userId).ConfigureAwait(false);
            if (userBalance.Balance < attraction.Cost)
                return BadRequest("Failed to buy ticket - not enough money");

            userBalance.Balance -= attraction.Cost;
            var userPurchase = new UserPurchase
            {
                Name = attraction.Name,
                ParkId = attraction.Park.Id,
                UserId = userId,
            };
            await dbContext.UserPurchases.AddAsync(userPurchase).ConfigureAwait(false);
            dbContext.UserBalances.Update(userBalance);
            await dbContext.SaveChangesAsync().ConfigureAwait(false);
            await transaction.CommitAsync().ConfigureAwait(false);
            
            return RedirectToAction("Profile", "Auth", new {id = userId});
        }
    }
}