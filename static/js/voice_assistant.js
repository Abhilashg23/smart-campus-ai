// Voice Assistant for Visitor Dashboard
// Features: Camera access, Face detection, Speech recognition, Indian voice synthesis

class VoiceAssistant {
    constructor() {
        // DOM Elements
        this.videoElement = document.getElementById('videoElement');
        this.backgroundVideo = document.getElementById('backgroundVideo');
        this.backgroundCanvas = document.getElementById('backgroundCanvas');
        this.faceCanvas = document.getElementById('faceCanvas');
        this.cameraOverlay = document.getElementById('cameraOverlay');
        this.faceStatus = document.getElementById('faceStatus');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.micBtn = document.getElementById('micBtn');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.conversationMessages = document.getElementById('conversationMessages');
        this.voiceIndicator = document.getElementById('voiceIndicator');

        // State
        this.isActive = false;
        this.isInAssistantMode = false;
        this.stream = null;
        this.faceDetected = false;
        this.hasGreeted = false;
        this.lastFaceSeenTime = 0;
        this.currentGreetedUserId = null;
        this.noFaceTimeout = null;
        this.isSpeaking = false; // Track if AI is currently speaking

        // Configuration
        this.FACE_LOST_TIMEOUT = 1000; // 1 second before returning to slideshow
        this.RECOGNITION_INTERVAL = 800; // Check every 0.8 seconds

        // Speech Recognition
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.indianVoice = null;

        // Initialize
        this.init();
    }

    init() {
        // Setup event listeners
        if (this.startBtn) this.startBtn.addEventListener('click', () => this.start());
        if (this.stopBtn) this.stopBtn.addEventListener('click', () => this.stop());

        // Setup speech recognition
        this.setupSpeechRecognition();

        // Find Indian voice
        this.findIndianVoice();

        // Auto-start camera and detection when page loads
        setTimeout(() => {
            this.autoStart();
        }, 1000);
    }

    async autoStart() {
        try {
            // Request camera access automatically
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            // Use background video element for monitoring while slideshow is visible
            if (this.backgroundVideo) {
                this.backgroundVideo.srcObject = this.stream;
                console.log('Background video initialized for face detection');
            }

            this.isActive = true;

            // Keep slideshow visible while monitoring
            if (this.statusIndicator) {
                this.statusIndicator.textContent = 'Monitoring';
                this.statusIndicator.classList.remove('offline');
                this.statusIndicator.classList.add('online');
            }

            // Start continuous face detection
            this.startContinuousFaceDetection();

        } catch (error) {
            console.error('Auto-start failed:', error);
        }
    }

    switchToAssistantMode() {
        if (this.isInAssistantMode) return;

        const slideshowSection = document.getElementById('slideshowSection');
        const assistantSection = document.getElementById('assistantSection');

        if (slideshowSection && assistantSection) {
            slideshowSection.style.display = 'none';
            assistantSection.style.display = 'block';
            this.isInAssistantMode = true;

            // Transfer video stream to main video element
            if (this.stream && this.videoElement) {
                this.videoElement.srcObject = this.stream;
                if (this.cameraOverlay) this.cameraOverlay.style.display = 'none';
                console.log('Switched to assistant mode with video');
            }

            // Start automatic listening
            this.startAutoListening();
        }
    }

    switchToSlideshowMode() {
        console.log('switchToSlideshowMode called, isInAssistantMode:', this.isInAssistantMode);

        if (!this.isInAssistantMode) return;

        const slideshowSection = document.getElementById('slideshowSection');
        const assistantSection = document.getElementById('assistantSection');
        const greetingOverlay = document.getElementById('greetingOverlay');

        if (slideshowSection && assistantSection) {
            slideshowSection.style.display = 'block';
            assistantSection.style.display = 'none';
            this.isInAssistantMode = false;

            // Reset greeting state for next visitor
            this.hasGreeted = false;
            this.currentGreetedUserId = null;
            this.faceDetected = false;
            this.isSpeaking = false;

            // Stop any ongoing speech
            if (this.synthesis) {
                this.synthesis.cancel();
            }

            // Stop listening
            this.stopAutoListening();

            // Clear any face status
            if (this.faceStatus) this.faceStatus.style.display = 'none';

            // Hide greeting overlay
            if (greetingOverlay) greetingOverlay.style.display = 'none';

            // Clear conversation messages
            if (this.conversationMessages) {
                this.conversationMessages.innerHTML = '<div class="welcome-message"><p>Welcome! I\'m your AI assistant.</p><p>Initializing conversation...</p></div>';
            }

            console.log('Switched back to slideshow mode');
        }
    }

    startAutoListening() {
        if (!this.recognition) return;
        if (this.isSpeaking) return; // Don't listen while speaking

        try {
            this.recognition.continuous = false; // Single utterance mode
            this.recognition.start();
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'flex';
            console.log('Auto listening started');
        } catch (e) {
            console.log('Recognition already started or error:', e);
        }
    }

    stopAutoListening() {
        if (!this.recognition) return;

        try {
            this.recognition.stop();
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'none';
            console.log('Auto listening stopped');
        } catch (e) {
            console.log('Error stopping recognition:', e);
        }
    }

    findIndianVoice() {
        const voices = this.synthesis.getVoices();
        this.indianVoice = voices.find(v => v.lang === 'en-IN') ||
            voices.find(v => v.lang === 'hi-IN') ||
            voices.find(v => v.lang.startsWith('en'));

        if (voices.length === 0) {
            this.synthesis.addEventListener('voiceschanged', () => {
                const newVoices = this.synthesis.getVoices();
                this.indianVoice = newVoices.find(v => v.lang === 'en-IN') ||
                    newVoices.find(v => v.lang === 'hi-IN') ||
                    newVoices.find(v => v.lang.startsWith('en'));
            });
        }
    }

    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error('Speech recognition not supported');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-IN';

        this.recognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript;
            this.handleUserSpeech(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            // Don't restart if speaking or aborted
            if (this.isInAssistantMode && event.error !== 'aborted' && !this.isSpeaking) {
                setTimeout(() => this.startAutoListening(), 2000);
            }
        };

        this.recognition.onend = () => {
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'none';
            // Only restart if in assistant mode, face detected, and not speaking
            if (this.isInAssistantMode && this.faceDetected && !this.isSpeaking) {
                setTimeout(() => this.startAutoListening(), 1500);
            }
        };
    }

    async start() {
        try {
            if (this.isActive) {
                if (this.startBtn) this.startBtn.style.display = 'none';
                if (this.stopBtn) this.stopBtn.style.display = 'flex';
                return;
            }

            this.stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            if (this.videoElement) this.videoElement.srcObject = this.stream;
            if (this.cameraOverlay) this.cameraOverlay.style.display = 'none';
            this.isActive = true;

            if (this.startBtn) this.startBtn.style.display = 'none';
            if (this.stopBtn) this.stopBtn.style.display = 'flex';
            if (this.statusIndicator) {
                this.statusIndicator.textContent = 'Monitoring';
                this.statusIndicator.classList.remove('offline');
                this.statusIndicator.classList.add('online');
            }

            if (this.conversationMessages) {
                this.conversationMessages.innerHTML = '';
                this.addMessage('Camera active. Waiting for guest...', 'assistant');
            }

            this.startContinuousFaceDetection();

        } catch (error) {
            console.error('Error accessing camera/microphone:', error);
            alert('Please allow camera and microphone access to use the voice assistant.');
        }
    }

    stop() {
        if (this.synthesis) this.synthesis.cancel();

        if (this.recognition) {
            try { this.recognition.stop(); } catch (e) { }
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }

        if (this.noFaceTimeout) {
            clearTimeout(this.noFaceTimeout);
            this.noFaceTimeout = null;
        }

        this.isActive = false;
        this.hasGreeted = false;
        this.faceDetected = false;
        this.currentGreetedUserId = null;

        this.switchToSlideshowMode();

        if (this.cameraOverlay) this.cameraOverlay.style.display = 'flex';
        if (this.stopBtn) this.stopBtn.style.display = 'none';
        if (this.micBtn) {
            this.micBtn.disabled = true;
            this.micBtn.classList.remove('listening');
        }
        if (this.statusIndicator) {
            this.statusIndicator.textContent = 'Offline';
            this.statusIndicator.classList.remove('online');
            this.statusIndicator.classList.add('offline');
        }
        if (this.faceStatus) this.faceStatus.style.display = 'none';
        if (this.voiceIndicator) this.voiceIndicator.style.display = 'none';

        // Restart auto-detection after a delay
        setTimeout(() => {
            if (!this.isActive) {
                this.autoStart();
            }
        }, 3000);
    }

    captureFrame() {
        return new Promise((resolve, reject) => {
            try {
                const activeVideo = (this.backgroundVideo && this.backgroundVideo.srcObject)
                    ? this.backgroundVideo
                    : this.videoElement;

                if (!activeVideo || !activeVideo.videoWidth) {
                    reject(new Error('No active video stream'));
                    return;
                }

                const canvas = this.backgroundCanvas || document.createElement('canvas');
                canvas.width = activeVideo.videoWidth;
                canvas.height = activeVideo.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(activeVideo, 0, 0);

                canvas.toBlob((blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Failed to capture frame'));
                    }
                }, 'image/jpeg', 0.8);
            } catch (error) {
                reject(error);
            }
        });
    }

    async recognizeFace() {
        try {
            const frameBlob = await this.captureFrame();
            const formData = new FormData();
            formData.append('image', frameBlob, 'frame.jpg');

            const response = await fetch('/api/face/recognize-visitor', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Face recognition error:', error);
            return { success: false, recognized: false };
        }
    }

    showGreeting(userName, userRole, isRegistered) {
        const greetingOverlay = document.getElementById('greetingOverlay');
        const greetingText = document.getElementById('greetingText');
        const greetingRole = document.getElementById('greetingRole');
        const greetingIcon = document.querySelector('.greeting-icon i');

        if (greetingOverlay && greetingText && greetingRole) {
            if (isRegistered) {
                greetingText.textContent = `Welcome back, ${userName}!`;
                greetingRole.textContent = userRole || 'Registered User';
                if (greetingIcon) greetingIcon.className = 'fas fa-user-check';
            } else {
                greetingText.textContent = `Welcome, Guest!`;
                greetingRole.textContent = 'Visitor';
                if (greetingIcon) greetingIcon.className = 'fas fa-user';
            }

            greetingOverlay.style.display = 'flex';

            // Hide greeting after 5 seconds
            setTimeout(() => {
                greetingOverlay.style.display = 'none';
            }, 5000);
        }
    }

    startContinuousFaceDetection() {
        let lastRecognitionTime = 0;

        const detectFace = async () => {
            if (!this.isActive) return;

            const now = Date.now();

            // Only check every RECOGNITION_INTERVAL
            if (now - lastRecognitionTime >= this.RECOGNITION_INTERVAL) {
                lastRecognitionTime = now;

                const result = await this.recognizeFace();
                console.log('Face recognition result:', result);

                // Check if face is actually detected (must be explicitly true)
                if (result.face_detected === true) {
                    console.log('✓ Face detected in frame');
                    // Face is present in frame
                    if (result.recognized && result.user) {
                        // Face recognized - registered user
                        this.handleFaceDetected(result.user, true, result.emotion);
                    } else {
                        // Face detected but not recognized = guest
                        // Always handle guest detection to update greeting/status
                        this.handleFaceDetected(null, false, result.emotion);
                    }
                } else {
                    console.log('✗ No face detected in frame');
                    // No face detected - start returning to slideshow
                    this.handleNoFaceDetected();
                }
            }

            requestAnimationFrame(detectFace);
        };

        detectFace();
    }

    handleFaceDetected(user, isRegistered, emotionData = null) {
        this.faceDetected = true;
        this.lastFaceSeenTime = Date.now();

        // Clear any pending timeout to switch back to slideshow
        if (this.noFaceTimeout) {
            clearTimeout(this.noFaceTimeout);
            this.noFaceTimeout = null;
        }

        // Switch to assistant mode if not already
        if (!this.isInAssistantMode) {
            this.switchToAssistantMode();
        }

        const userId = user ? user.id : 'guest';

        // Always update face status badge to show current person
        if (isRegistered && user) {
            const firstName = user.first_name || user.full_name.split(' ')[0];
            if (this.faceStatus) {
                this.faceStatus.innerHTML = `<i class="fas fa-check"></i> ${firstName} Recognized`;
                this.faceStatus.style.display = 'block';
                this.faceStatus.style.background = 'rgba(16,185,129,0.9)';
            }
        } else {
            // Guest/Visitor
            if (this.faceStatus) {
                this.faceStatus.innerHTML = '<i class="fas fa-user"></i> Guest Detected';
                this.faceStatus.style.display = 'block';
                this.faceStatus.style.background = 'rgba(59,130,246,0.9)';
            }
        }

        // Only greet once per user session
        if (!this.hasGreeted || this.currentGreetedUserId !== userId) {
            this.hasGreeted = true;
            this.currentGreetedUserId = userId;

            // Generate emotion-based greeting addition
            let emotionGreeting = '';
            if (emotionData && emotionData.greeting_message) {
                emotionGreeting = ' ' + emotionData.greeting_message;
            }

            if (isRegistered && user) {
                // Registered user
                const firstName = user.first_name || user.full_name.split(' ')[0];
                this.showGreeting(firstName, user.role, true);

                // Speak greeting with emotion
                const greeting = `Namaste ${firstName}! Welcome back to Government Science College ( Autonomous ) Hassan smart campus, I'm your campus assistant.${emotionGreeting} How can I help you today?`;
                this.addMessage(greeting, 'assistant');
                setTimeout(() => this.speak(greeting), 500);

                console.log('Greeted registered user:', user.full_name, 'Emotion:', emotionData);
            } else {
                // Guest/Visitor
                this.showGreeting('Guest', 'Visitor', false);

                const greeting = `Namaste! Welcome to Government Science College ( Autonomous ) Hassan smart campus, I'm your campus assistant.${emotionGreeting} How can I assist you today?`;
                this.addMessage(greeting, 'assistant');
                setTimeout(() => this.speak(greeting), 500);

                console.log('Greeted guest visitor', 'Emotion:', emotionData);
            }
        }
    }

    handleNoFaceDetected() {
        // Only start timeout if we're in assistant mode and haven't already started one
        if (this.isInAssistantMode && !this.noFaceTimeout) {
            console.log('No face detected, starting timeout to return to slideshow...');

            // Mark face as not detected immediately
            this.faceDetected = false;

            this.noFaceTimeout = setTimeout(() => {
                console.log('Face lost timeout reached, returning to slideshow');
                this.switchToSlideshowMode();
                this.noFaceTimeout = null;
            }, this.FACE_LOST_TIMEOUT);
        }
    }

    toggleListening() {
        if (!this.recognition) {
            alert('Speech recognition is not supported in your browser.');
            return;
        }

        if (!this.faceDetected) {
            alert('Please look at the camera. I need to see your face to assist you.');
            return;
        }

        if (this.micBtn && this.micBtn.classList.contains('listening')) {
            this.recognition.stop();
            this.micBtn.classList.remove('listening');
        } else {
            this.recognition.start();
            if (this.micBtn) this.micBtn.classList.add('listening');
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'flex';
        }
    }

    handleUserSpeech(transcript) {
        if (this.voiceIndicator) this.voiceIndicator.style.display = 'none';

        if (!this.faceDetected) {
            const warning = "I can't see you. Please look at the camera.";
            this.addMessage(warning, 'assistant');
            this.speak(warning);
            return;
        }

        this.addMessage(transcript, 'user');
        this.getAIResponse(transcript);
    }

    async getAIResponse(message) {
        if (!this.faceDetected) {
            const warning = "Please look at the camera so I can assist you.";
            this.addMessage(warning, 'assistant');
            this.speak(warning);
            return;
        }

        try {
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'flex';

            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'none';

            if (data.response) {
                if (!this.faceDetected) {
                    const warning = "I have your answer, but please look at the camera.";
                    this.addMessage(warning, 'assistant');
                    this.speak(warning);
                    return;
                }

                this.addMessage(data.response, 'assistant');
                this.speak(data.response);
            }
        } catch (error) {
            console.error('Error getting AI response:', error);
            if (this.voiceIndicator) this.voiceIndicator.style.display = 'none';
            const errorMsg = 'Sorry, I encountered an error. Please try again.';
            this.addMessage(errorMsg, 'assistant');
            this.speak(errorMsg);
        }
    }

    speak(text) {
        if (!this.synthesis) {
            console.error('Speech synthesis not available');
            return;
        }

        // Stop listening while speaking
        this.isSpeaking = true;
        this.stopAutoListening();
        this.synthesis.cancel();

        setTimeout(() => {
            const utterance = new SpeechSynthesisUtterance(text);

            if (this.indianVoice) {
                utterance.voice = this.indianVoice;
            }

            utterance.lang = 'en-IN';
            utterance.rate = 1.1;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            utterance.onstart = () => {
                console.log('Speech started');
                this.isSpeaking = true;
            };
            utterance.onerror = (event) => {
                console.error('Speech error:', event);
                this.isSpeaking = false;
                // Restart listening after error
                if (this.isInAssistantMode && this.faceDetected) {
                    setTimeout(() => this.startAutoListening(), 1000);
                }
            };
            utterance.onend = () => {
                console.log('Speech finished');
                this.isSpeaking = false;
                // Restart listening after speech ends
                if (this.isInAssistantMode && this.faceDetected) {
                    setTimeout(() => this.startAutoListening(), 1000);
                }
            };

            try {
                this.synthesis.speak(utterance);
            } catch (error) {
                console.error('Error speaking:', error);
                this.isSpeaking = false;
            }
        }, 100);
    }

    addMessage(text, type) {
        if (!this.conversationMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const label = document.createElement('div');
        label.className = `message-label ${type}`;
        label.innerHTML = type === 'user' ?
            '<i class="fas fa-user"></i> You' :
            'AI Assistant';

        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = text;

        messageDiv.appendChild(label);
        messageDiv.appendChild(content);

        this.conversationMessages.appendChild(messageDiv);
        this.conversationMessages.scrollTop = this.conversationMessages.scrollHeight;
    }
}

// Initialize voice assistant when DOM is loaded
let voiceAssistantInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('videoElement')) {
        voiceAssistantInstance = new VoiceAssistant();
    }
});

// Cleanup on page unload/refresh
window.addEventListener('beforeunload', () => {
    if (voiceAssistantInstance && voiceAssistantInstance.isActive) {
        voiceAssistantInstance.stop();
    }
});

// Cleanup on navigation
window.addEventListener('pagehide', () => {
    if (voiceAssistantInstance && voiceAssistantInstance.isActive) {
        voiceAssistantInstance.stop();
    }
});

// Stop assistant when user navigates away
document.addEventListener('visibilitychange', () => {
    if (document.hidden && voiceAssistantInstance && voiceAssistantInstance.isActive) {
        voiceAssistantInstance.stop();
    }
});
