using System.Diagnostics;
using System.Text;
using System.Threading.Tasks;
using CtfLand.Service.Models;
using CtfLand.Service.Providers;
using Microsoft.AspNetCore.Mvc;

namespace CtfLand.Service.Controllers
{
    [Route("")]
    public class HomeController : Controller
    {
        private readonly ILandingTemplateProvider landingTemplateProvider;

        public HomeController(ILandingTemplateProvider landingTemplateProvider)
        {
            this.landingTemplateProvider = landingTemplateProvider;
        }

        [Route("")]
        public IActionResult Index()
        {
            return View();
        }

        [Route("Error")]
        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
