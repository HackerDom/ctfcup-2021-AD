using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Abstractions;
using Microsoft.AspNetCore.Mvc.ModelBinding;
using Microsoft.AspNetCore.Mvc.Razor;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.AspNetCore.Mvc.ViewFeatures;
using Microsoft.AspNetCore.Server.IIS.Core;
using RouteData = Microsoft.AspNetCore.Routing.RouteData;

namespace CtfLand.Service.Providers
{
    public class TemplateRenderer
    {
        private readonly IRazorViewEngine viewEngine;
        private readonly IHttpContextAccessor httpContextAccessor;
        private readonly ITempDataProvider tempDataProvider;

        public TemplateRenderer(
            IRazorViewEngine viewEngine,
            IHttpContextAccessor httpContextAccessor,
            ITempDataProvider tempDataProvider)
        {
            this.viewEngine = viewEngine;
            this.httpContextAccessor = httpContextAccessor;
            this.tempDataProvider = tempDataProvider;
        }

        public async Task<string> RenderTemplate<TModel>(string template, TModel model)
        {
            var filePath = $"Views/Landing/Landing-{Guid.NewGuid()}.cshtml";
            var fileInfo = new FileInfo(filePath);
            await File.WriteAllTextAsync(fileInfo.FullName, template, Encoding.UTF8);

            try
            {
                return await RenderTemplateFromFile($"~/{filePath}", model)
                    .ConfigureAwait(false);
            }
            finally
            {
                fileInfo.Delete();
            }
        }

        private async Task<string> RenderTemplateFromFile<TModel>(string viewName, TModel model)
        {
            var viewEngineResult = viewEngine.GetView(null, viewName, false);
            if (viewEngineResult.View == null)
                throw new Exception("Could not find the View file. Searched locations:\r\n" + string.Join("\r\n", viewEngineResult.SearchedLocations));

            var view = viewEngineResult.View;
            var actionContext = new ActionContext(httpContextAccessor.HttpContext!, new RouteData(), new ActionDescriptor());

            await using var outputStringWriter = new StringWriter();
            var viewContext = new ViewContext(
                actionContext,
                view,
                new ViewDataDictionary<TModel>(new EmptyModelMetadataProvider(), new ModelStateDictionary())
                {
                    Model = model,
                },
                new TempDataDictionary(actionContext.HttpContext, tempDataProvider),
                outputStringWriter,
                new HtmlHelperOptions());

            var renderResult = await TaskRunner.RunWithTimeout(
                    () => view.RenderAsync(viewContext),
                    TimeSpan.FromSeconds(3))
                .ConfigureAwait(false);

            var result = outputStringWriter.ToString();
            return renderResult.IsSuccess && !string.IsNullOrEmpty(result)
                ? result
                : null;
        }
    }
}