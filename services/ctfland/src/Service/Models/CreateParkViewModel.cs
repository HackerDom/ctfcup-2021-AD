namespace CtfLand.Service.Models
{
    public record CreateParkViewModel : CreateParkRequestModel
    {
        public string[] AllowedAttractionVariables { get; set; }

        public string[] AllowedDescVariables { get; set; }
    }
}