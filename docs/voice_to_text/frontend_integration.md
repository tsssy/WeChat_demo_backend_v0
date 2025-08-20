# 语音转文字功能 - 前端集成指南

## 概述

本文档详细说明了前端如何集成语音转文字功能，包括音频采集、接口调用、错误处理和用户体验优化。

## 接口概览

### 主要接口

1. **语音转文字**: `POST /api/v1/voice/transcribe`
2. **语音聊天**: `POST /api/v1/voice/chat` (推荐)
3. **健康检查**: `GET /api/v1/voice/health`

### 推荐使用方式

**对于大多数应用场景，建议直接使用语音聊天接口**，因为它提供了完整的语音交互体验。

## HTML5 原生实现

### 完整示例代码

```html
<!DOCTYPE html>
<html>
<head>
    <title>语音转文字测试</title>
    <style>
        .container { max-width: 800px; margin: 50px auto; padding: 20px; }
        .button { padding: 15px 30px; margin: 10px; font-size: 16px; cursor: pointer; }
        .recording { background: red; color: white; }
        .result { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .audio-player { margin: 10px 0; }
        .status { margin: 20px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>语音转文字测试</h1>
        
        <!-- 用户信息 -->
        <div>
            <label>用户ID: <input type="number" id="userId" value="123" /></label>
            <label>性别: 
                <select id="gender">
                    <option value="neutral">中性</option>
                    <option value="male">男性</option>
                    <option value="female">女性</option>
                </select>
            </label>
        </div>
        
        <!-- 录音控制 -->
        <div>
            <button id="startRecord" class="button">开始录音</button>
            <button id="stopRecord" class="button" disabled>停止录音</button>
            <button id="playRecord" class="button" disabled>播放录音</button>
        </div>
        
        <!-- 音频播放器 -->
        <div class="audio-player">
            <audio id="audioPlayer" controls style="display: none;"></audio>
        </div>
        
        <!-- 功能按钮 -->
        <div>
            <button id="transcribeBtn" class="button" disabled>转写音频</button>
            <button id="chatBtn" class="button" disabled>语音聊天</button>
        </div>
        
        <!-- 结果显示 -->
        <div id="result" class="result" style="display: none;"></div>
        
        <!-- 状态显示 -->
        <div id="status" class="status">准备就绪</div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let audioBlob;
        
        // 获取DOM元素
        const startBtn = document.getElementById('startRecord');
        const stopBtn = document.getElementById('stopRecord');
        const playBtn = document.getElementById('playRecord');
        const transcribeBtn = document.getElementById('transcribeBtn');
        const chatBtn = document.getElementById('chatBtn');
        const audioPlayer = document.getElementById('audioPlayer');
        const resultDiv = document.getElementById('result');
        const statusDiv = document.getElementById('status');
        
        // 开始录音
        startBtn.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = () => {
                    audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    audioPlayer.src = URL.createObjectURL(audioBlob);
                    audioPlayer.style.display = 'block';
                    
                    // 启用相关按钮
                    playBtn.disabled = false;
                    transcribeBtn.disabled = false;
                    chatBtn.disabled = false;
                    
                    updateStatus('录音完成，可以播放或转写');
                };
                
                mediaRecorder.start();
                startBtn.disabled = true;
                stopBtn.disabled = false;
                startBtn.classList.add('recording');
                
                updateStatus('正在录音...');
                
            } catch (error) {
                updateStatus('无法访问麦克风: ' + error.message);
            }
        });
        
        // 停止录音
        stopBtn.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                
                startBtn.disabled = false;
                stopBtn.disabled = true;
                startBtn.classList.remove('recording');
                
                updateStatus('录音已停止');
            }
        });
        
        // 播放录音
        playBtn.addEventListener('click', () => {
            audioPlayer.play();
        });
        
        // 转写音频
        transcribeBtn.addEventListener('click', async () => {
            if (!audioBlob) {
                updateStatus('请先录音');
                return;
            }
            
            await transcribeAudio(audioBlob);
        });
        
        // 语音聊天
        chatBtn.addEventListener('click', async () => {
            if (!audioBlob) {
                updateStatus('请先录音');
                return;
            }
            
            await voiceChat(audioBlob);
        });
        
        // 语音转文字函数
        async function transcribeAudio(audioBlob) {
            try {
                updateStatus('正在转写音频...');
                
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                formData.append('user_id', document.getElementById('userId').value);
                
                const response = await fetch('/api/v1/voice/transcribe', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showResult('转写结果', {
                        '用户说的话': result.text,
                        '检测语言': result.language,
                        '置信度': result.confidence?.toFixed(2) || 'N/A',
                        '处理时间': result.processing_time + '秒'
                    });
                    updateStatus('转写完成');
                } else {
                    throw new Error(result.error || '转写失败');
                }
                
            } catch (error) {
                updateStatus('转写失败: ' + error.message);
                console.error('转写错误:', error);
            }
        }
        
        // 语音聊天函数
        async function voiceChat(audioBlob) {
            try {
                updateStatus('正在进行语音聊天...');
                
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                formData.append('user_id', document.getElementById('userId').value);
                formData.append('gender', document.getElementById('gender').value);
                
                const response = await fetch('/api/v1/voice/chat', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showResult('聊天结果', {
                        '用户说的话': result.transcribed_text,
                        'AI回复': result.ai_response,
                        '总结': result.summary,
                        '置信度': result.confidence?.toFixed(2) || 'N/A',
                        '总处理时间': result.processing_time + '秒'
                    });
                    updateStatus('语音聊天完成');
                } else {
                    throw new Error(result.error || '语音聊天失败');
                }
                
            } catch (error) {
                updateStatus('语音聊天失败: ' + error.message);
                console.error('聊天错误:', error);
            }
        }
        
        // 显示结果
        function showResult(title, data) {
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
                <h3>${title}</h3>
                ${Object.entries(data).map(([key, value]) => 
                    `<p><strong>${key}:</strong> ${value}</p>`
                ).join('')}
            `;
        }
        
        // 更新状态
        function updateStatus(message) {
            statusDiv.textContent = message;
            console.log(message);
        }
    </script>
</body>
</html>
```

## React 组件实现

### 核心组件代码

```jsx
import React, { useState, useRef } from 'react';
import './VoiceToText.css';

const VoiceToText = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState('准备就绪');
    const [loading, setLoading] = useState(false);
    
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    
    // 用户配置
    const [userId, setUserId] = useState(123);
    const [gender, setGender] = useState('neutral');
    
    // 开始录音
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];
            
            mediaRecorderRef.current.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };
            
            mediaRecorderRef.current.onstop = () => {
                const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                setAudioBlob(blob);
                setStatus('录音完成');
            };
            
            mediaRecorderRef.current.start();
            setIsRecording(true);
            setStatus('正在录音...');
            
        } catch (error) {
            setStatus('无法访问麦克风: ' + error.message);
        }
    };
    
    // 停止录音
    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);
        }
    };
    
    // 语音聊天
    const voiceChat = async () => {
        if (!audioBlob) return;
        
        setLoading(true);
        setStatus('正在进行语音聊天...');
        
        try {
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.wav');
            formData.append('user_id', userId);
            formData.append('gender', gender);
            
            const response = await fetch('/api/v1/voice/chat', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                setResult({
                    type: 'chat',
                    data: result
                });
                setStatus('语音聊天完成');
            } else {
                throw new Error(result.error || '语音聊天失败');
            }
            
        } catch (error) {
            setStatus('聊天失败: ' + error.message);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="voice-container">
            <h1>语音转文字</h1>
            
            {/* 用户配置 */}
            <div className="user-config">
                <label>
                    用户ID: 
                    <input 
                        type="number" 
                        value={userId} 
                        onChange={(e) => setUserId(Number(e.target.value))}
                    />
                </label>
                <label>
                    性别: 
                    <select value={gender} onChange={(e) => setGender(e.target.value)}>
                        <option value="neutral">中性</option>
                        <option value="male">男性</option>
                        <option value="female">女性</option>
                    </select>
                </label>
            </div>
            
            {/* 录音控制 */}
            <div className="recording-controls">
                <button 
                    onClick={startRecording} 
                    disabled={isRecording}
                    className="btn btn-primary"
                >
                    开始录音
                </button>
                <button 
                    onClick={stopRecording} 
                    disabled={!isRecording}
                    className="btn btn-danger"
                >
                    停止录音
                </button>
            </div>
            
            {/* 音频播放器 */}
            {audioBlob && (
                <div className="audio-player">
                    <audio controls src={URL.createObjectURL(audioBlob)} />
                </div>
            )}
            
            {/* 功能按钮 */}
            <div className="action-buttons">
                <button 
                    onClick={voiceChat} 
                    disabled={!audioBlob || loading}
                    className="btn btn-info"
                >
                    {loading ? '处理中...' : '语音聊天'}
                </button>
            </div>
            
            {/* 状态显示 */}
            <div className="status">{status}</div>
            
            {/* 结果显示 */}
            {result && (
                <div className="result">
                    <h3>聊天结果</h3>
                    <p><strong>用户说的话:</strong> {result.data.transcribed_text}</p>
                    <p><strong>AI回复:</strong> {result.data.ai_response}</p>
                    <p><strong>总结:</strong> {result.data.summary || '无'}</p>
                    <p><strong>置信度:</strong> {result.data.confidence?.toFixed(2) || 'N/A'}</p>
                    <p><strong>总处理时间:</strong> {result.data.processing_time}秒</p>
                </div>
            )}
        </div>
    );
};

export default VoiceToText;
```

## Vue 3 组件实现

### 核心组件代码

```vue
<template>
  <div class="voice-container">
    <h1>语音转文字</h1>
    
    <!-- 用户配置 -->
    <div class="user-config">
      <label>
        用户ID: 
        <input type="number" v-model="userId" />
      </label>
      <label>
        性别: 
        <select v-model="gender">
          <option value="neutral">中性</option>
          <option value="male">男性</option>
          <option value="female">女性</option>
        </select>
      </label>
    </div>
    
    <!-- 录音控制 -->
    <div class="recording-controls">
      <button 
        @click="startRecording" 
        :disabled="isRecording"
        class="btn btn-primary"
      >
        开始录音
      </button>
      <button 
        @click="stopRecording" 
        :disabled="!isRecording"
        class="btn btn-danger"
      >
        停止录音
      </button>
    </div>
    
    <!-- 音频播放器 -->
    <div v-if="audioBlob" class="audio-player">
      <audio controls :src="audioUrl" />
    </div>
    
    <!-- 功能按钮 -->
    <div class="action-buttons">
      <button 
        @click="voiceChat" 
        :disabled="!audioBlob || loading"
        class="btn btn-info"
      >
        {{ loading ? '处理中...' : '语音聊天' }}
      </button>
    </div>
    
    <!-- 状态显示 -->
    <div class="status">{{ status }}</div>
    
    <!-- 结果显示 -->
    <div v-if="result" class="result">
      <h3>聊天结果</h3>
      <p><strong>用户说的话:</strong> {{ result.data.transcribed_text }}</p>
      <p><strong>AI回复:</strong> {{ result.data.ai_response }}</p>
      <p><strong>总结:</strong> {{ result.data.summary || '无' }}</p>
      <p><strong>置信度:</strong> {{ result.data.confidence?.toFixed(2) || 'N/A' }}</p>
      <p><strong>总处理时间:</strong> {{ result.data.processing_time }}秒</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 响应式数据
const isRecording = ref(false)
const audioBlob = ref(null)
const result = ref(null)
const status = ref('准备就绪')
const loading = ref(false)
const userId = ref(123)
const gender = ref('neutral')

// 计算属性
const audioUrl = computed(() => {
  return audioBlob.value ? URL.createObjectURL(audioBlob.value) : ''
})

// 录音相关
let mediaRecorder = null
let audioChunks = []

// 开始录音
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []
    
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data)
    }
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/wav' })
      audioBlob.value = blob
      status.value = '录音完成'
    }
    
    mediaRecorder.start()
    isRecording.value = true
    status.value = '正在录音...'
    
  } catch (error) {
    status.value = '无法访问麦克风: ' + error.message
  }
}

// 停止录音
const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
    isRecording.value = false
  }
}

// 语音聊天
const voiceChat = async () => {
  if (!audioBlob.value) return
  
  loading.value = true
  status.value = '正在进行语音聊天...'
  
  try {
    const formData = new FormData()
    formData.append('audio_file', audioBlob.value, 'recording.wav')
    formData.append('user_id', userId.value)
    formData.append('gender', gender.value)
    
    const response = await fetch('/api/v1/voice/chat', {
      method: 'POST',
      body: formData
    })
    
    const resultData = await response.json()
    
    if (resultData.status === 'success') {
      result.value = {
        type: 'chat',
        data: resultData
      }
      status.value = '语音聊天完成'
    } else {
      throw new Error(resultData.error || '语音聊天失败')
    }
    
  } catch (error) {
    status.value = '聊天失败: ' + error.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.voice-container {
  max-width: 800px;
  margin: 50px auto;
  padding: 20px;
}

.user-config {
  margin: 20px 0;
}

.user-config label {
  margin-right: 20px;
}

.recording-controls, .action-buttons {
  margin: 20px 0;
}

.btn {
  padding: 15px 30px;
  margin: 10px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 5px;
}

.btn-primary { background: #007bff; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-info { background: #17a2b8; color: white; }

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.audio-player {
  margin: 20px 0;
}

.status {
  margin: 20px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
}

.result {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: #f9f9f9;
}
</style>
```

## 关键实现要点

### 1. 音频采集

```javascript
// 获取麦克风权限
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// 创建录音器
const mediaRecorder = new MediaRecorder(stream);

// 收集音频数据
mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
};

// 录音完成
mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    // 现在可以发送到后端了
};
```

### 2. 数据传输

```javascript
// 创建FormData
const formData = new FormData();
formData.append('audio_file', audioBlob, 'recording.wav');
formData.append('user_id', userId);
formData.append('gender', gender);

// 发送到后端
const response = await fetch('/api/v1/voice/chat', {
    method: 'POST',
    body: formData
});
```

### 3. 错误处理

```javascript
try {
    const response = await fetch('/api/v1/voice/chat', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.status === 'success') {
        // 处理成功结果
    } else {
        throw new Error(result.error || '请求失败');
    }
    
} catch (error) {
    console.error('请求失败:', error);
    // 显示错误信息给用户
}
```

## 移动端适配

### 1. 响应式设计

```css
@media (max-width: 768px) {
    .voice-container {
        margin: 20px;
        padding: 15px;
    }
    
    .btn {
        width: 100%;
        margin: 5px 0;
    }
    
    .user-config label {
        display: block;
        margin: 10px 0;
    }
}
```

### 2. 触摸优化

```javascript
// 添加触摸事件支持
button.addEventListener('touchstart', (e) => {
    e.preventDefault();
    // 触摸反馈
});

button.addEventListener('touchend', (e) => {
    e.preventDefault();
    // 执行操作
});
```

## 使用建议

1. **开发测试**: 使用HTML5原生版本，快速验证功能
2. **生产环境**: 使用React/Vue组件，更好的用户体验
3. **移动端**: 确保响应式设计和触摸优化
4. **错误处理**: 完整的错误提示和用户反馈

## 总结

前端集成语音转文字功能主要涉及：
1. 音频采集（MediaRecorder API）
2. 文件上传（FormData）
3. 接口调用（fetch API）
4. 结果展示和错误处理

推荐使用语音聊天接口，因为它提供了完整的语音交互体验，包括转写、AI回复和对话历史管理。
