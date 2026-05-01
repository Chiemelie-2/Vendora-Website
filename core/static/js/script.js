// static/js/main.js
function search() {
    let query = document.getElementById("searchInput").value;
    
    // Fetch results from the backend search view
    fetch(`/restaurants/search?q=${query}`)
        .then(res => res.text())
        .then(data => {
            // Replace the restaurant list with filtered results
            document.getElementById("restaurantList").innerHTML = data;
        })
        .catch(err => console.error("Search failed:", err));
}
