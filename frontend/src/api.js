const API_URL = "http://127.0.0.1:8001";

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