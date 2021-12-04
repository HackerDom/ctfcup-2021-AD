using System;
using CtfLand.DataLayer;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service.Providers
{
    public class UserProvider
    {
        private readonly DbContext dbContext;

        public UserProvider(DbContext dbContext)
        {
            this.dbContext = dbContext;
        }

        public User GetUser(Guid id)
        {
            return dbContext.Users.Find(id);
        }
    }
}