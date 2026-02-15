const API = "http://localhost:5050/api/dramas";

async function loadDramas() {
    const res = await fetch(API);
    const data = await res.json();

    const list = document.getElementById("drama-list");
    list.innerHTML = "";

    data.forEach(d => {
        list.innerHTML += `
            <div class="card">
                <img src="${d.poster}" alt="">
                <h3>${d.title}</h3>
                <p><b>${d.year}</b> • ${d.genre}</p>
                <p>${d.description}</p>
                <button onclick="deleteDrama(${d.id})">Hapus</button>
            </div>
        `;
    });
}

async function addDrama() {
    const drama = {
        title: document.getElementById("title").value,
        year: document.getElementById("year").value,
        genre: document.getElementById("genre").value,
        description: document.getElementById("description").value,
        poster: document.getElementById("poster").value
    };

    await fetch(API, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(drama)
    });

    loadDramas();
}

async function deleteDrama(id) {
    await fetch(`${API}/${id}`, { method: "DELETE" });
    loadDramas();
}

loadDramas();
