using CtfLand.DataLayer.Models;
using Microsoft.EntityFrameworkCore;

namespace CtfLand.DataLayer
{
    public class DbContext : Microsoft.EntityFrameworkCore.DbContext
    {
        public DbContext(DbContextOptions<DbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users { get; set; }

        public DbSet<Park> Parks { get; set; }

        public DbSet<Attraction> Attractions { get; set; }

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);

            builder.Entity<User>(entity => entity.HasIndex(u => u.Login).IsUnique());
            builder.Entity<Park>(entity => entity.HasIndex(u => u.Name).IsUnique());
        }
    }
}
