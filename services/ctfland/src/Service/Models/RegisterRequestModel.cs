using System.ComponentModel.DataAnnotations;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service.Models
{
    public class RegisterRequestModel
    {
        [Required(ErrorMessage = "Не указан логин")]
        public string Login { get; set; }

        [Required(ErrorMessage = "Не указан пароль")]
        [DataType(DataType.Password)]
        public string Password { get; set; }

        [Required(ErrorMessage = "Не указан пароль второй раз")]
        [DataType(DataType.Password)]
        [Compare(nameof(Password), ErrorMessage = "Пароли не совпадают")]
        public string RepeatedPassword { get; set; }

        [Required(ErrorMessage = "Не выбрана роль")]
        public UserRole Role { get; set; } = UserRole.Moderator;

        [Required(ErrorMessage = "Не указаны паспортные данные")]
        public string Document { get; set; }
    }
}