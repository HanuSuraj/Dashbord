// script.js

// Handle the login form submission
document.getElementById('login-form')?.addEventListener('submit', function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        alert('Please fill in both fields.');
    } else {
        // Perform login logic (e.g., AJAX request to the backend)
        console.log('Logging in...');
    }
});

// Handle the register form submission
document.getElementById('register-form')?.addEventListener('submit', function (event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!username || !email || !password) {
        alert('Please fill in all fields.');
    } else {
        // Perform registration logic (e.g., AJAX request to the backend)
        console.log('Registering...');
    }
});

// Fetch news articles
window.onload = function () {
    const newsContainer = document.querySelector('.container');
    if (newsContainer) {
        fetch('/api/news/')
            .then(response => response.json())
            .then(data => {
                data.articles.forEach(article => {
                    const articleCard = document.createElement('div');
                    articleCard.classList.add('article-card');

                    articleCard.innerHTML = `
                        <h3 class="article-title">${article.title}</h3>
                        <p class="article-author">By ${article.author || 'Unknown'}</p>
                        <p class="article-publishedAt">${article.publishedAt}</p>
                        <p class="article-description">${article.description || 'No description available.'}</p>
                        <a class="article-link" href="${article.url}" target="_blank">Read more</a>
                    `;

                    newsContainer.appendChild(articleCard);
                });
            })
            .catch(error => {
                console.error('Error fetching news:', error);
            });
    }
};

// Function to filter articles based on search input, author, and date
function filterArticles() {
    const searchInput = document.getElementById('author');
    const articles = document.querySelectorAll('.article-card');

    searchInput.addEventListener('input', function () {
        const query = searchInput.value.toLowerCase();

        articles.forEach(article => {
            const title = article.querySelector('.article-title').textContent.toLowerCase();
            const author = article.querySelector('.article-author').textContent.toLowerCase();

            // Show or hide the article based on search query
            if (author.includes(query) || title.includes(query)) {
                article.style.display = 'block';
            } else {
                article.style.display = 'none';
            }
        });
    });
}
