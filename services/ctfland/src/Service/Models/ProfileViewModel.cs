using System.Collections.Generic;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service.Models
{
    public class PurchaseViewModel
    {
        public string AttractionName { get; set; }
        
        public string TicketKey { get; set; }
    }
    
    public class ProfileViewModel
    {
        public User User { get; set; }
        
        public int? CurrentBalance { get; set; }
        
        public ICollection<PurchaseViewModel> Purchases { get; set; }
    }
}