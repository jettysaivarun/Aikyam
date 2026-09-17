const API_URL = "https://aikyam-backend-1x1c.onrender.com";

export async function getMaterials() {
    const response = await fetch(
        `${API_URL}/materials`
    );

    if (!response.ok) {
        throw new Error("Failed to load materials");
    }

    return response.json();
}


export async function simulate(data) {

    const response = await fetch(
        `${API_URL}/simulate`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)
        }
    );

    if (!response.ok) {
        throw new Error("Simulation failed");
    }

    return response.json();
}