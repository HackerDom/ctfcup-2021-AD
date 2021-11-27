using System;
using System.Linq;
using System.Threading.Tasks;
using CtfLand.DataLayer.Models;
using Microsoft.EntityFrameworkCore;
using DbContext = CtfLand.DataLayer.DbContext;

namespace CtfLand.Service.Providers
{
    public interface IParksProvider
    {
        Task<Park> GetPark(Guid id);
        Park[] GetParks(int skip, int take, bool isPublicOnly, Guid? ownerId);
    }

    public class ParksProvider : IParksProvider
    {
        private readonly DbContext dbContext;

        public ParksProvider(DbContext dbContext)
        {
            this.dbContext = dbContext;
        }
        
        public async Task<Park> GetPark(Guid id)
        {
            return await dbContext.Parks
                .AsQueryable()
                .Include(park => park.Owner)
                .Include(park => park.Attractions)
                .FirstOrDefaultAsync(park => park.Id == id)
                .ConfigureAwait(false);
        }


        public Park[] GetParks(int skip, int take, bool isPublicOnly, Guid? ownerId)
        {
            return dbContext.Parks
                .AsQueryable()
                .Include(park => park.Owner)
                .Include(park => park.Attractions)
                .AsEnumerable()
                .Where(park => ownerId is null || park.Owner.Id == ownerId)
                .Where(park => !isPublicOnly || park.IsPublic)
                .OrderByDescending(park => park.CreatedAt)
                .Skip(skip)
                .Take(take)
                .ToArray();
        }
    }
}