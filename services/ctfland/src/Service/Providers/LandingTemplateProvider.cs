using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CtfLand.DataLayer.Models;
using CtfLand.Service.Models;

namespace CtfLand.Service.Providers
{
    public interface ILandingTemplateProvider
    {
        Task<string> GetLandingTemplate(CreateParkRequestModel createTemplateRequestModel);

        public string[] GetAllowedAttractionVariables { get; }

        public string[] GetAllowedDescVariables { get; }
    }

    public class LandingTemplateProvider : ILandingTemplateProvider
    {
        private const string LandingTemplateFilePath = "Views/ParkLandingTemplate.cshtml";
        private const string AttractionPrefix = "@attraction.";

        private static readonly Dictionary<string, string> AllowedDescVariables = new()
        {
            ["$userLogin"] = "@userProvider.GetUser(Model.UserId).Login",
        };

        private static readonly Dictionary<string, string> AllowedAttractionVariables = new()
        {
            ["$name"] = $"{AttractionPrefix}{nameof(Attraction.Name)}",
            ["$desc"] = $"{AttractionPrefix}{nameof(Attraction.Description)}",
            ["$cost"] = $"{AttractionPrefix}{nameof(Attraction.Cost)}",
        };

        private readonly TemplateRenderer templateRenderer;

        public LandingTemplateProvider(TemplateRenderer templateRenderer)
        {
            this.templateRenderer = templateRenderer;
        }

        public string[] GetAllowedDescVariables => AllowedDescVariables.Keys.ToArray();
        public string[] GetAllowedAttractionVariables => AllowedAttractionVariables.Keys.ToArray();

        public async Task<string> GetLandingTemplate(CreateParkRequestModel createTemplateRequestModel)
        {
            var patchedModel = createTemplateRequestModel with
            {
                Description = FormatTextWithVariables(createTemplateRequestModel.Description, AllowedDescVariables),
                HtmlAttractionBlock = FormatTextWithVariables(createTemplateRequestModel.HtmlAttractionBlock, AllowedAttractionVariables),
            };
            var template = await File.ReadAllTextAsync(LandingTemplateFilePath, Encoding.UTF8).ConfigureAwait(false);
            return await templateRenderer.RenderTemplate(template, patchedModel).ConfigureAwait(false);
        }

        private static string FormatTextWithVariables(string text, Dictionary<string, string> variables)
        {
            var result = text.Replace("@", "@@");
            return variables.Aggregate(
                result,
                (acc, pair) => acc.Replace(pair.Key, pair.Value));
        }
    }
}