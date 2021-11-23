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
        [RegularExpression(@"^[\d\w\.@+\-_\(\), ]+$", ErrorMessage = "Можно указать только Email или телефонный номер")]
        public string Contact { get; set; }

        [Required]
        [Range(0, 100000, ErrorMessage = "Максимальное количество посетителей должно быть в диапазоне от 0 до 100 000")]
        public int MaxVisitorsCount { get; set; }

        [Required]
        public string HtmlAttractionBlock { get; set; }
    }
}