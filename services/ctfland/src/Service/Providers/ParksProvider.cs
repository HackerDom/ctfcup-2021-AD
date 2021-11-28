using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CtfLand.DataLayer.Models;
using Microsoft.EntityFrameworkCore;
using DbContext = CtfLand.DataLayer.DbContext;

namespace CtfLand.Service.Providers
{
    public class ParksListFilter
    {
        public bool IsPublicOnly { get; set; }
        public Guid? OwnerId { get; set; }
        
        public ParksListFilter(bool isPublicOnly, Guid? ownerId)
        {
            IsPublicOnly = isPublicOnly;
            OwnerId = ownerId;
        }
    }
    
    public interface IParksProvider
    {
        Task<Park> GetPark(Guid id);
        Task<IList<Park>> GetParks(int skip, int take, ParksListFilter filter);
        Task<int> Count(ParksListFilter filter);
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


        public async Task<IList<Park>> GetParks(int skip, int take, ParksListFilter filter)
        {
            return await dbContext.Parks
                .AsQueryable()
                .Include(park => park.Owner)
                .Include(park => park.Attractions)
                .Where(park => filter.OwnerId == null || park.Owner.Id == filter.OwnerId)
                .Where(park => !filter.IsPublicOnly || park.IsPublic)
                .OrderByDescending(park => park.CreatedAt)
                .Skip(skip)
                .Take(take)
                .ToListAsync();
        }

        public async Task<int> Count(ParksListFilter filter)
        {
            return await dbContext.Parks
                .AsQueryable()
                .Include(park => park.Owner)
                .Include(park => park.Attractions)
                .Where(park => filter.OwnerId == null || park.Owner.Id == filter.OwnerId)
                .Where(park => !filter.IsPublicOnly || park.IsPublic)
                .OrderByDescending(park => park.CreatedAt)
                .CountAsync();
        }
    }
}