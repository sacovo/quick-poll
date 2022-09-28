const fetchHelper = (url) => {
  return new Promise((resolve, reject) => {
    fetch(url).then((response) => {
      if (!response.ok) reject(response.statusText);
      response.json().then(resolve).catch(reject);
    });
  });
};

const fetchData = () => {
  return fetchHelper("/data/");
};

const fetchPast = () => {
  return fetchHelper("/past/");
};

const postData = (url, data) => {
  const csrfToken = document.querySelector(
    'input[name="csrfmiddlewaretoken"]'
  ).value;
  const formData = new FormData();

  for (entry in data) {
    formData.set(entry, data[entry]);
  }

  return new Promise((resolve, reject) => {
    fetch(url, {
      method: "post",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      body: formData,
    }).then((response) => {
      if (!response.ok) reject(response.statusText);
      resolve("success");
    });
  });
};
