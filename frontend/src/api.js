const API_URL =
  import.meta.env.VITE_API_URL ||
  "https://aikyam-backend-1x1c.onrender.com";


async function request(
  path,
  options = {}
) {

  const response = await fetch(
    `${API_URL}${path}`,
    {
      headers: {
        "Content-Type":
          "application/json",

        ...(options.headers || {}),
      },

      ...options,
    }
  );


  if (!response.ok) {

    let message =
      `Request failed (${response.status})`;

    try {

      const body =
        await response.json();

      message =
        body.detail ||
        message;

    } catch {

      // Ignore JSON parsing error.
    }

    throw new Error(
      message
    );
  }


  return response.json();
}


export const getMaterials =
  () =>
    request(
      "/materials"
    );


export const getClimates =
  () =>
    request(
      "/climates"
    );


export const getLocations =
  () =>
    request(
      "/locations"
    );


export const simulate =
  (data) =>
    request(
      "/simulate",
      {
        method: "POST",

        body:
          JSON.stringify(data),
      }
    );


export const optimize =
  (data) =>
    request(
      "/optimize",
      {
        method: "POST",

        body:
          JSON.stringify(data),
      }
    );


export const compare =
  (data) =>
    request(
      "/compare",
      {
        method: "POST",

        body:
          JSON.stringify(data),
      }
    );