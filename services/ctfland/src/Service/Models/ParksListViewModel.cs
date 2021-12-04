using System.Collections.Generic;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service.Models
{
    public class ParksListViewModel
    {
        public int TotalCount { get; set; }
        public ICollection<Park> Parks { get; set; }
    }
}