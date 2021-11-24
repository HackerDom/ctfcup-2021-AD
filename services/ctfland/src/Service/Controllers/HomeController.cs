using Microsoft.AspNetCore.Mvc;

namespace CtfLand.Service.Controllers
{
    [Route("")]
    public class HomeController : Controller
    {
        [Route("")]
        public IActionResult Index()
        {
            return View();
        }
    }
}
