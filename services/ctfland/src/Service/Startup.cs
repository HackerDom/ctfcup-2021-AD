using System;
using CtfLand.DataLayer.Models;
using CtfLand.Service.Providers;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using DbContext = CtfLand.DataLayer.DbContext;

namespace CtfLand.Service
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public void ConfigureServices(IServiceCollection services)
        {
            var host = Environment.GetEnvironmentVariable("POSTGRES_HOST") ?? "localhost";
            var port = Environment.GetEnvironmentVariable("POSTGRES_PORT") ?? "5432";
            var database = Environment.GetEnvironmentVariable("POSTGRES_DB_NAME") ?? "ctfland";
            var user = Environment.GetEnvironmentVariable("POSTGRES_USER") ?? "ctfland";
            var password = Environment.GetEnvironmentVariable("POSTGRES_PASSWORD") ?? "ctfland";
            var connectionString = $"Host={host};Port={port};Database={database};Username={user};Password={password}";

            services.AddDbContext<DbContext>(options =>
            {
                options.UseNpgsql(connectionString);
            });
            services.AddDatabaseDeveloperPageExceptionFilter();

            services.AddAuthorization();
            services
                .AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
                .AddCookie(options =>
                {
                    options.LoginPath = new PathString("/auth/login");
                    options.LogoutPath = new PathString("/auth/logout");
                    options.AccessDeniedPath = new PathString("/auth/forbidden");
                });

            services.AddControllersWithViews();

            services.AddRazorPages()
                .AddRazorRuntimeCompilation();

            services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();
            services.AddTransient<TemplateRenderer>();
            services.AddScoped<UserProvider>();
            services.AddSingleton<ILandingTemplateProvider, LandingTemplateProvider>();
            services.AddSingleton<HashPasswordProvider>();
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseMigrationsEndPoint();
            }
            else
            {
                app.UseExceptionHandler("/Error");
            }

            app.UseStaticFiles();

            app.UseRouting();

            app.UseAuthentication();
            app.UseAuthorization();

            app.UseEndpoints(endpoints => endpoints.MapControllers());
        }
    }
}
