import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../src/App';

// Mock axios
jest.mock('axios');
import axios from 'axios';

const mockAxios = axios;

describe('App Component', () => {
  beforeEach(() => {
    // Clear localStorage
    localStorage.clear();
  });

  test('renders chatbot interface', () => {
    render(<App />);
    expect(screen.getByText('AI Chatbot Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  test('sends message and receives response', async () => {
    mockAxios.post.mockResolvedValue({
      data: { bot_response: 'Hello! How can I help you?' }
    });

    render(<App />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
    });
  });

  test('handles API error', async () => {
    mockAxios.post.mockRejectedValue(new Error('Network error'));

    render(<App />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Sorry, I encountered an error. Please try again.')).toBeInTheDocument();
    });
  });

  test('toggles dark mode', () => {
    render(<App />);

    const darkModeButton = screen.getByText('🌙 Dark');
    fireEvent.click(darkModeButton);

    expect(screen.getByText('☀️ Light')).toBeInTheDocument();
  });

  test('clears chat', () => {
    render(<App />);

    const clearButton = screen.getByText('Clear Chat');
    fireEvent.click(clearButton);

    // Should show welcome message
    expect(screen.getByText('Welcome to AI Chatbot Assistant!')).toBeInTheDocument();
  });
});
