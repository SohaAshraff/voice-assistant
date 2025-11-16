import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';

export default function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('Disconnected');
  const [transcript, setTranscript] = useState([]);
  
  const roomRef = useRef(null);
  const audioRef = useRef(null);
  const transcriptEndRef = useRef(null);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const addMessage = (speaker, text) => {
    const timestamp = new Date().toLocaleTimeString();
    setTranscript(prev => [...prev, { speaker, text, timestamp }]);
  };

  const connect = async () => {
    setIsConnecting(true);
    setError(null);
    setStatus('Connecting...');
    setTranscript([]);

    try {
      const response = await fetch('http://localhost:5000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_name: 'voice-ai-room',
          participant_name: `user_${Date.now()}`
        })
      });

      if (!response.ok) throw new Error('Failed to get token');
      const { token, url } = await response.json();

      const room = new Room();
      roomRef.current = room;

      room.on(RoomEvent.Connected, () => {
        setIsConnected(true);
        setIsConnecting(false);
        setStatus('Connected - You can speak now!');
        addMessage('system', '✅ Connected to voice assistant');
      });

      room.on(RoomEvent.Disconnected, () => {
        setIsConnected(false);
        setStatus('Disconnected');
        addMessage('system', '❌ Disconnected from assistant');
      });

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === Track.Kind.Audio) {
          const element = track.attach();
          if (audioRef.current) {
            audioRef.current.innerHTML = '';
            audioRef.current.appendChild(element);
          }
        }
      });

      room.on(RoomEvent.TranscriptionReceived, (segments, participant) => {
        segments.forEach(segment => {
          const isUser = participant && participant.identity.startsWith('user');
          addMessage(isUser ? 'user' : 'assistant', segment.text);
        });
      });

      await room.connect(url, token);
      await room.localParticipant.setMicrophoneEnabled(true);
      addMessage('system', '🎤 Microphone enabled - Start speaking!');
      
    } catch (err) {
      setError(err.message);
      setStatus('Connection failed');
      setIsConnecting(false);
      addMessage('system', `❌ Error: ${err.message}`);
    }
  };

  const disconnect = async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect();
      roomRef.current = null;
      setIsConnected(false);
      setStatus('Disconnected');
    }
  };

  useEffect(() => {
    return () => {
      if (roomRef.current) roomRef.current.disconnect();
    };
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    }}>
      <div style={{
        display: 'flex',
        maxWidth: '1200px',
        width: '100%',
        gap: '40px'
      }}>
        {/* LEFT SIDE - Controls and Info */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ textAlign: 'center' }}>
            <h1 style={{ margin: '0 0 10px 0', fontSize: '32px', color: '#fff' }}>
              🎙️ Store Assistant
            </h1>
            <p style={{ margin: 0, color: '#eee', fontSize: '14px' }}>
              Voice-powered AI assistant with live transcript
            </p>
          </div>

          {/* Status */}
          <div style={{
            background: isConnected ? '#d4edda' : '#f8f9fa',
            border: `2px solid ${isConnected ? '#28a745' : '#dee2e6'}`,
            borderRadius: '12px',
            padding: '20px',
            textAlign: 'center',
            color: isConnected ? '#155724' : '#495057',
            fontWeight: '600'
          }}>
            {status}
          </div>

          {/* Error */}
          {error && (
            <div style={{
              background: '#f8d7da',
              border: '2px solid #f5c6cb',
              borderRadius: '12px',
              padding: '15px',
              color: '#721c24',
              fontSize: '14px'
            }}>
              ⚠️ {error}
            </div>
          )}

          {/* Connect / Disconnect Button */}
          {!isConnected ? (
            <button
              onClick={connect}
              disabled={isConnecting}
              style={{
                width: '100%',
                padding: '18px',
                fontSize: '18px',
                fontWeight: '600',
                border: 'none',
                borderRadius: '12px',
                background: isConnecting ? '#6c757d' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                cursor: isConnecting ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
              }}
            >
              {isConnecting ? '⏳ Connecting...' : '🎤 Connect to Assistant'}
            </button>
          ) : (
            <button
              onClick={disconnect}
              style={{
                width: '100%',
                padding: '18px',
                fontSize: '18px',
                fontWeight: '600',
                border: 'none',
                borderRadius: '12px',
                background: '#dc3545',
                color: 'white',
                cursor: 'pointer',
                boxShadow: '0 4px 15px rgba(220, 53, 69, 0.4)'
              }}
            >
              📞 Disconnect
            </button>
          )}

          {/* Instructions */}
          <div style={{
            marginTop: '20px',
            padding: '15px',
            background: '#f8f9fa',
            borderRadius: '12px',
            fontSize: '13px',
            color: '#495057'
          }}>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#333' }}>
              💡 How to use:
            </div>
            <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
              <li>Click "Connect to Assistant"</li>
              <li>Allow microphone access when prompted</li>
              <li>Start speaking naturally - your conversation will appear on the right</li>
              <li>Ask about store hours, location, services, or any questions</li>
            </ul>
          </div>
        </div>

        {/* RIGHT SIDE - Transcript Box */}
        <div style={{
          width: '400px',
          height: '600px',
          background: '#fff',
          borderRadius: '20px',
          padding: '20px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px'
        }}>
          {transcript.length === 0 ? (
            <div style={{
              textAlign: 'center',
              color: '#999',
              marginTop: '50%',
              fontSize: '14px'
            }}>
              <p style={{ fontSize: '24px', marginBottom: '10px' }}>👋</p>
              <p>No conversation yet</p>
              <p style={{ fontSize: '12px', marginTop: '5px' }}>
                Connect and start speaking to see the transcript
              </p>
            </div>
          ) : (
            transcript.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: 
                    msg.speaker === 'system' ? '#e3f2fd' :
                    msg.speaker === 'user' ? '#fff' :
                    '#f3e5f5',
                  border: 
                    msg.speaker === 'system' ? '1px solid #90caf9' :
                    msg.speaker === 'user' ? '2px solid #667eea' :
                    '2px solid #ba68c8',
                  maxWidth: '100%',
                  wordBreak: 'break-word'
                }}
              >
                {msg.speaker !== 'system' && (
                  <div style={{
                    fontSize: '11px',
                    fontWeight: '600',
                    color: '#666',
                    marginBottom: '6px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    {msg.speaker === 'user' ? '👤 You' : '🤖 Assistant'} 
                    <span style={{ 
                      marginLeft: '8px', 
                      fontWeight: '400',
                      color: '#999'
                    }}>
                      {msg.timestamp}
                    </span>
                  </div>
                )}
                <div style={{
                  color: msg.speaker === 'system' ? '#1976d2' : '#333',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  fontStyle: msg.speaker === 'system' ? 'italic' : 'normal'
                }}>
                  {msg.text}
                </div>
              </div>
            ))
          )}
          <div ref={transcriptEndRef} />
        </div>

        <div ref={audioRef} style={{ display: 'none' }} />
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}
