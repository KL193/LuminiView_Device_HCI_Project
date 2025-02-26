const express = require('express');
const mongoose = require('mongoose');

const app = express();
const PORT = 3000;

// MongoDB connection
mongoose.connect('mongodb+srv://hci_user:oUoaJXKsn2MFCeHU@cluster0.gbt6n.mongodb.net/face_detection_db?retryWrites=true&w=majority&appName=Cluster0', {
                    
    
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
.then(() => console.log('MongoDB Connected'))
.catch(err => console.error('MongoDB Connection Error:', err));

mongoose.connection.once('open', () => {
    console.log('Connected to DB:', mongoose.connection.db.databaseName);
});

// Mongoose Schema
const detectionSchema = new mongoose.Schema({
    status: String,
    timestamp: String
});

// Explicitly specify the collection name if needed
const Detection = mongoose.model('detection_status', detectionSchema, 'detection_status');

// API to get last 20 records and analyze status
app.get('/status', async (req, res) => {
    try {
        const last20Records = await Detection.find().sort({ _id: -1 }).limit(5);
        //here 5 have to change in to 20
        console.log('Last 20 Records:', last20Records); // Log records to check data

        // Check if the collection has records
        if (last20Records.length === 0) {
            return res.status(404).json({ message: 'No records found' });
        }

        // Check if any status is 'No Face Detected'
        const hasNoFace = last20Records.some(record => record.status === 'No Face Detected');

        // Respond 0 if any "No Face Detected", otherwise 1
        const responseStatus = hasNoFace ? 0 : 1;

        return res.json({ status: responseStatus, total_records_checked: last20Records.length });
    } catch (error) {
        console.error('Error:', error);
        return res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
});


