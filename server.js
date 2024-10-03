const express = require('express');
const { spawn } = require('child_process');

const app = express();
const port = process.env.PORT || 5000;

app.use(express.static('static'));
app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/templates/index.html');
});

app.post('/recommend', (req, res) => {
    const user_index = req.body.user_index;
    const num_recommendations = req.body.num_recommendations;

    const pythonProcess = spawn('python', ['app.py', user_index, num_recommendations]);

    pythonProcess.stdout.on('data', (data) => {
        const recommendations = data.toString().split('\n').filter(Boolean);
        res.send({ recommendations });
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(data.toString());
        res.status(500).send('Error generating recommendations');
    });
});

app.post('/common_recommendations', (req, res) => {
    const num_common_recommendations = req.body.num_common_recommendations;

    const pythonProcess = spawn('python', ['app.py', num_common_recommendations]);

    pythonProcess.stdout.on('data', (data) => {
        const common_recommendations = data.toString().split('\n').filter(Boolean);
        res.send({ common_recommendations });
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(data.toString());
        res.status(500).send('Error generating common recommendations');
    });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
