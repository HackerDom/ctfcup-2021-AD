using System.Collections.Generic;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service.Models
{
    public class ParksListViewModel
    {
        public ICollection<Park> Parks { get; set; }
    }
}