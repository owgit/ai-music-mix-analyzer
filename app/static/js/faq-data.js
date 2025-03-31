/**
 * FAQ data for Mix Analyzer
 * This data is used for the FAQ modal and FAQ schema structured data
 */
const faqData = [
    {
        question: "What audio formats are supported by Mix Analyzer?",
        answer: "Mix Analyzer supports MP3, WAV, FLAC, AIFF, AIF, M4A, and PCM audio formats for free analysis."
    },
    {
        question: "How does the AI-powered analysis work?",
        answer: "Our artificial intelligence analyzes your audio file across multiple dimensions including frequency balance, dynamic range, stereo field, clarity, harmonic content, and transients. The AI then provides personalized recommendations based on genre-specific best practices."
    },
    {
        question: "Is my audio data kept private?",
        answer: "Yes. Your uploaded audio files are processed on our secure servers and are not shared with third parties. Files are automatically deleted after processing is complete."
    },
    {
        question: "How accurate is the frequency spectrum analysis?",
        answer: "Our frequency analysis uses industry-standard FFT (Fast Fourier Transform) algorithms to provide professional-grade spectral analysis with high accuracy across the full frequency spectrum."
    },
    {
        question: "What is the maximum file size I can upload?",
        answer: "Mix Analyzer accepts audio files up to 50MB in size for free analysis."
    },
    {
        question: "Does Mix Analyzer work on mobile devices?",
        answer: "Yes, Mix Analyzer is fully responsive and works on smartphones and tablets, allowing you to analyze your mixes on the go."
    },
    {
        question: "What should I select for 'instrumental track'?",
        answer: "Select this option if your track contains no vocals. This helps our AI provide more relevant frequency analysis and EQ recommendations tailored to instrumental music."
    },
    {
        question: "How can I interpret the mix score?",
        answer: "The mix score is a numerical evaluation from 0-100 that represents the overall quality of your mix based on industry standards. Scores above 80 indicate professional quality, while scores below 60 suggest areas for improvement."
    }
];

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { faqData };
} 