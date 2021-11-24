using System.ComponentModel.DataAnnotations;

namespace CtfLand.Service.Models
{
    public record CreateParkRequestModel
    {
        [Required]
        [RegularExpression(@"[\w\s\d\-]+")]
        public string Name { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        [Email(ErrorMessage = "Invalid email")]
        public string Email { get; set; }

        [Required]
        [Range(0, 100000, ErrorMessage = "Максимальное количество посетителей должно быть в диапазоне от 0 до 100 000")]
        public int MaxVisitorsCount { get; set; }

        [Required]
        public string HtmlAttractionBlock { get; set; }
        
        [Required]
        public bool IsPublic { get; set; }
    }
}