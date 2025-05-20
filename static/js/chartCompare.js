    let myChart = null;
    let typeChart = null;


    async function sendSelection(button, metric) {
        const allButtons = document.querySelectorAll('.chart-btn');
        allButtons.forEach(btn => btn.classList.remove('active'));

        // Thêm class 'active' vào nút đang được nhấn
        button.classList.add('active');


        // currentMetric = metric;
        if(metric === 'calories' || metric === 'caffeine') {
            typeChart = 'bar';
        }
        else {
            typeChart = 'doughnut'
        }

        const response = await fetch('/get_data', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ drink: selectedOptionsKey, metric: metric })
                        });

        const result = await response.json();

        // Dữ liệu
        const data = {
            labels: selectedOptionsKey,
            values: result,
        };

        const ctx = document.getElementById('myChart').getContext('2d');

        if (myChart) {
            myChart.destroy();
        }



        myChart = new Chart(ctx, {
            type: typeChart,
            data: {
                labels: data.labels,
                datasets: [{
                    label: `${metric} per drink`,
                    data: data.values,
                    backgroundColor: selectedOptionsColor
                }]
            },
            options: {
              maintainAspectRatio: false,
              responsive: true
            }
        });
    }
