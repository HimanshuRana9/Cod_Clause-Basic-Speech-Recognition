import React, {useState, useRef, useEffect} from 'react';
import { Button, Paper, Typography } from '@mui/material';
import { io } from 'socket.io-client';

export default function LiveRecorder(){
  const [msgs, setMsgs] = useState([]);
  const socketRef = useRef(null);
  const mediaRef = useRef(null);

  useEffect(()=>{
    socketRef.current = io('/', { transports:['websocket'] });
    socketRef.current.on('connect', ()=>append('WS connected'));
    socketRef.current.on('partial', data => append('Partial: ' + (data.text||'')));
    socketRef.current.on('final', data => append('Final: ' + (data.text||'') + ' | action: ' + JSON.stringify(data.action_result)));
    socketRef.current.on('session_started', ()=>append('Session started on server'));
    socketRef.current.on('disconnect', ()=>append('WS disconnected'));
    return ()=>{
      try{ socketRef.current.disconnect(); }catch(e){}
    };
  }, []);

  const append = (m) => setMsgs(prev => [...prev, m]);

  const start = async () => {
    append('Requesting microphone...');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio:true});
      const options = { mimeType: 'audio/webm;codecs=opus' };
      const mr = new MediaRecorder(stream, options);
      mediaRef.current = {mr, stream};
      mr.ondataavailable = e => {
        if (e.data && e.data.size > 0) {
          e.data.arrayBuffer().then(buf => {
            socketRef.current.emit('audio_chunk', buf);
          });
        }
      };
      mr.onstart = ()=>{
        append('Recording started');
        socketRef.current.emit('start_session', {});
      };
      mr.onstop = ()=>{
        append('Recording stopped - sending stop signal');
        socketRef.current.emit('stop_session', {});
        try{ mediaRef.current.stream.getTracks().forEach(t=>t.stop()); }catch(e){}
        mediaRef.current = null;
      };
      mr.start(250);
      mr.stream = stream;
    } catch (err) {
      append('Mic error: ' + String(err));
    }
  };

  const stop = () => {
    const cur = mediaRef.current;
    if (cur && cur.mr && cur.mr.state === 'recording') cur.mr.stop();
    else append('Not recording');
  };

  return (
    <Paper sx={{p:2}}>
      <Typography variant='h6'>Live Recorder (WebSocket)</Typography>
      <Button variant='contained' onClick={start} sx={{mr:1}}>Start</Button>
      <Button variant='outlined' onClick={stop}>Stop</Button>
      <div style={{marginTop:12}}>
        {msgs.map((m,i)=>(<div key={i}>{m}</div>))}
      </div>
    </Paper>
  );
}
