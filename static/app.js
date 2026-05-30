function startDownload() {

    let urls = document
        .getElementById("urls")
        .value
        .split("\n")
        .filter(x => x.trim() !== "");

    fetch("/start", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            urls: urls
        })

    });

    monitorProgress();
}


function monitorProgress() {

    let timer = setInterval(() => {

        fetch("/progress")
            .then(res => res.json())
            .then(data => {

                let percent = 0;

                if (data.total > 0) {

                    percent = Math.round(
                        (data.current / data.total) * 100
                    );

                }

                let bar =
                    document.getElementById(
                        "progressBar"
                    );

                bar.style.width =
                    percent + "%";

                bar.innerHTML =
                    percent + "%";

                loadHistory();

                if (
                    data.status ===
                    "completed"
                ) {

                    clearInterval(timer);

                    window.location.href =
                        "/download-zip";

                }

            });

    }, 1000);
}


function loadHistory() {

    fetch("/history")
        .then(res => res.json())
        .then(data => {

            let table =
                document.getElementById(
                    "historyTable"
                );

            table.innerHTML = "";

            data.forEach(item => {

                table.innerHTML += `
                    <tr>
                        <td>${item.file}</td>
                        <td>${item.status}</td>
                    </tr>
                `;

            });

        });

}