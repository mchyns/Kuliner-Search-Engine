document.addEventListener('DOMContentLoaded', function() {
    // Animasi untuk logo pada halaman utama
    const logo = document.querySelector('.logo h1');
    if (logo) {
        logo.style.opacity = '0';
        logo.style.transform = 'translateY(-20px)';
        logo.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        
        setTimeout(() => {
            logo.style.opacity = '1';
            logo.style.transform = 'translateY(0)';
        }, 300);
    }
    
    // Animasi untuk kotak pencarian
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        searchBox.style.opacity = '0';
        searchBox.style.transform = 'translateY(-20px)';
        searchBox.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        
        setTimeout(() => {
            searchBox.style.opacity = '1';
            searchBox.style.transform = 'translateY(0)';
        }, 500);
    }
    
    // Animasi untuk tag pencarian populer
    const popularSearches = document.querySelector('.popular-searches');
    if (popularSearches) {
        popularSearches.style.opacity = '0';
        popularSearches.style.transition = 'opacity 0.8s ease';
        
        setTimeout(() => {
            popularSearches.style.opacity = '1';
        }, 700);
    }
    
    // Animasi untuk kartu hasil pencarian
    const resultCards = document.querySelectorAll('.result-card');
    if (resultCards.length > 0) {
        resultCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * index);
        });
    }
});