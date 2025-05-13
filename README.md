const createExam = async (examData) => {
    try {
        const response = await axios.post('/api/exams/create/', examData, {
            headers: {
                'Authorization': `Bearer ${token}` // Assuming token-based auth
            }
        });

        if (response.data.success) {
            // Redirect to add questions page
            history.push(`/exams/${response.data.exam_id}/add-questions`);
        } else {
            // Handle error
            toast.error(response.data.message);
        }
    } catch (error) {
        console.error('Exam creation failed:', error);
        toast.error('Failed to create exam');
    }
};