"use client";

import { useCallback, useState } from "react";
import { useChatContext, chatActions } from "@/components/providers/ChatContext";
import { useAudioContext, audioActions } from "@/components/providers/AudioContext";
import { VoiceButton } from "@/components/voice/VoiceButton";
import { AudioPlayer } from "@/components/voice/AudioPlayer";
import { InputArea } from "@/components/chat/InputArea";
import { MuteToggle } from "@/components/voice/MuteToggle";
import { MicrophoneIcon, LoadingSpinner, CloseIcon } from "@/components/shared/Icons";
import { sendVoiceMessage, sendTextMessage, synthesizeSpeech } from "@/lib/api";

/**
 * Main chat area container component.
 * Contains message list, input area, and voice controls.
 */
export function ChatArea() {
  const { state: chatState, dispatch: chatDispatch } = useChatContext();
  const { state: audioState, dispatch: audioDispatch } = useAudioContext();

  // Current response audio blob for playback
  const [responseAudio, setResponseAudio] = useState<Blob | null>(null);
  const [lastMessageId, setLastMessageId] = useState<number | null>(null);

  /**
   * Handle completed voice recording.
   * Note: Voice messages are handled by the orchestrator which returns audio only.
   * The transcribed text is not available in the response, so we show a placeholder.
   */
  const handleRecordingComplete = useCallback(
    async (audioBlob: Blob) => {
      chatDispatch(chatActions.setSending(true));
      chatDispatch(chatActions.clearError());
      setResponseAudio(null);

      // Generate message IDs
      const userMessageId = Date.now();
      const assistantMessageId = userMessageId + 1;

      // Add placeholder user message (voice input)
      chatDispatch(
        chatActions.addMessage({
          id: userMessageId,
          role: "user",
          content: "🎤 音声メッセージ",
          created_at: new Date().toISOString(),
        })
      );

      try {
        // Send to orchestrator
        const response = await sendVoiceMessage(
          audioBlob,
          chatState.currentConversationId ?? undefined
        );

        // Add assistant message placeholder (audio response)
        chatDispatch(
          chatActions.addMessage({
            id: assistantMessageId,
            role: "assistant",
            content: "🔊 音声応答",
            created_at: new Date().toISOString(),
          })
        );

        // Play the response audio
        setResponseAudio(response.audio);
        setLastMessageId(assistantMessageId);
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "音声の処理中にエラーが発生しました";
        chatDispatch(chatActions.setError(errorMessage));
      } finally {
        chatDispatch(chatActions.setSending(false));
      }
    },
    [chatState.currentConversationId, chatDispatch]
  );

  /**
   * Handle text message submission.
   */
  const handleTextMessage = useCallback(
    async (text: string) => {
      chatDispatch(chatActions.setSending(true));
      chatDispatch(chatActions.clearError());
      setResponseAudio(null);

      // Generate message IDs
      const userMessageId = Date.now();
      const assistantMessageId = userMessageId + 1;

      // Add user message immediately
      chatDispatch(
        chatActions.addMessage({
          id: userMessageId,
          role: "user",
          content: text,
          created_at: new Date().toISOString(),
        })
      );

      try {
        // Send text to LLM
        const response = await sendTextMessage(
          text,
          chatState.currentConversationId ?? undefined
        );

        // Add assistant message
        chatDispatch(
          chatActions.addMessage({
            id: assistantMessageId,
            role: "assistant",
            content: response.response,
            created_at: new Date().toISOString(),
          })
        );

        // Update conversation ID if this was a new conversation
        if (!chatState.currentConversationId && response.conversationId) {
          chatDispatch(chatActions.selectConversation(response.conversationId));
        }

        // Synthesize speech for the response
        if (response.response && !audioState.isMuted) {
          const { audio } = await synthesizeSpeech(response.response);
          setResponseAudio(audio);
          setLastMessageId(assistantMessageId);
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "メッセージの送信中にエラーが発生しました";
        chatDispatch(chatActions.setError(errorMessage));
      } finally {
        chatDispatch(chatActions.setSending(false));
      }
    },
    [chatState.currentConversationId, audioState.isMuted, chatDispatch]
  );

  /**
   * Handle mute toggle.
   */
  const handleMuteToggle = useCallback(() => {
    audioDispatch(audioActions.toggleMute());
  }, [audioDispatch]);

  /**
   * Handle playback end.
   */
  const handlePlaybackEnd = useCallback(() => {
    // Audio finished playing - could trigger UI updates here
  }, []);

  /**
   * Handle playback error.
   */
  const handlePlaybackError = useCallback(
    (error: string) => {
      chatDispatch(chatActions.setError(`音声再生エラー: ${error}`));
    },
    [chatDispatch]
  );

  return (
    <div className="flex h-full flex-col bg-white dark:bg-zinc-900">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-700">
        <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          Voice Chat
        </h1>
        <MuteToggle
          isMuted={audioState.isMuted}
          onToggle={handleMuteToggle}
          disabled={audioState.playbackState === "playing"}
        />
      </header>

      {/* Message List Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {chatState.messages.length === 0 && !chatState.isSending ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
                <MicrophoneIcon className="h-8 w-8 text-blue-500" />
              </div>
              <p className="text-lg text-zinc-700 dark:text-zinc-300">
                マイクボタンを押して話しかけてください
              </p>
              <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                または、下のテキスト入力欄からメッセージを送信できます
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Messages will be rendered here by MessageList in US2 */}
            {chatState.messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Loading indicator during voice processing */}
        {chatState.isSending && (
          <div className="mt-4 flex items-center justify-center">
            <div className="flex items-center gap-3 rounded-lg bg-zinc-50 px-4 py-3 dark:bg-zinc-800">
              <LoadingSpinner className="h-5 w-5 text-blue-500" />
              <span className="text-zinc-600 dark:text-zinc-300">
                処理中...
              </span>
            </div>
          </div>
        )}

        {/* Audio player for response */}
        <AudioPlayer
          audioBlob={responseAudio}
          autoPlay={true}
          muted={audioState.isMuted}
          messageId={lastMessageId ?? undefined}
          showControls={audioState.playbackState === "playing"}
          onPlaybackEnd={handlePlaybackEnd}
          onError={handlePlaybackError}
        />
      </div>

      {/* Error display */}
      {chatState.error && (
        <div className="border-t border-red-200 bg-red-50 px-4 py-3 dark:border-red-800 dark:bg-red-900/20">
          <div className="flex items-center justify-between">
            <p className="text-sm text-red-700 dark:text-red-400">
              {chatState.error}
            </p>
            <button
              type="button"
              onClick={() => chatDispatch(chatActions.clearError())}
              className="text-red-500 hover:text-red-700 dark:hover:text-red-300"
              aria-label="エラーを閉じる"
            >
              <CloseIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      {/* Recording indicator */}
      {audioState.isRecording && (
        <div className="border-t border-red-200 bg-red-50 px-4 py-2 dark:border-red-800 dark:bg-red-900/20">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 animate-pulse rounded-full bg-red-500" />
            <span className="text-sm text-red-700 dark:text-red-400">
              録音中... マイクボタンをもう一度押すと送信します
            </span>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-zinc-200 p-4 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          {/* Voice button */}
          <VoiceButton
            onRecordingComplete={handleRecordingComplete}
            disabled={chatState.isSending}
            loading={chatState.isSending}
          />

          {/* Text input */}
          <InputArea
            onSend={handleTextMessage}
            disabled={chatState.isSending}
            isRecording={audioState.isRecording}
            className="flex-1"
          />
        </div>
      </div>
    </div>
  );
}
