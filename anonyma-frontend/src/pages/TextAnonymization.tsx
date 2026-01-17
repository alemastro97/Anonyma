import React, { useState } from 'react';
import { anonymaApi } from '../services/api';
import { AnonymizeTextResponse, Detection } from '../types';

const TextAnonymization: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [mode, setMode] = useState<'redact' | 'substitute' | 'visual_redact'>(
    'redact'
  );
  const [language, setLanguage] = useState('it');
  const [useFlair, setUseFlair] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnonymizeTextResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnonymize = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to anonymize');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await anonymaApi.anonymizeText({
        text: inputText,
        mode,
        language,
        use_flair: useFlair,
      });
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to anonymize text');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setInputText('');
    setResult(null);
    setError(null);
  };

  const handleCopyResult = () => {
    if (result?.anonymized_text) {
      navigator.clipboard.writeText(result.anonymized_text);
    }
  };

  const exampleTexts = [
    {
      label: 'Italian Example',
      text: 'Mario Rossi (mario.rossi@email.com) abita a Milano in Via Roma 123. Il suo numero di telefono è +39 339 1234567.',
    },
    {
      label: 'English Example',
      text: 'John Smith (john.smith@company.com) lives in New York at 123 Main Street. His phone number is +1 555-123-4567.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Text Anonymization</h2>
        <p className="mt-2 text-sm text-gray-600">
          Detect and anonymize personally identifiable information (PII) in text
        </p>
      </div>

      {/* Configuration Panel */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Mode Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Anonymization Mode
            </label>
            <select
              value={mode}
              onChange={(e) =>
                setMode(e.target.value as 'redact' | 'substitute' | 'visual_redact')
              }
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option value="redact">Redact (replace with labels)</option>
              <option value="substitute">Substitute (replace with fake data)</option>
              <option value="visual_redact">Visual Redact (black boxes)</option>
            </select>
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option value="it">Italian</option>
              <option value="en">English</option>
            </select>
          </div>

          {/* Flair Toggle */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Advanced AI
            </label>
            <div className="flex items-center h-10">
              <input
                type="checkbox"
                checked={useFlair}
                onChange={(e) => setUseFlair(e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Use Flair NER (slower, more accurate)
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Examples */}
      <div className="flex flex-wrap gap-2">
        <span className="text-sm font-medium text-gray-700">Quick examples:</span>
        {exampleTexts.map((example, idx) => (
          <button
            key={idx}
            onClick={() => setInputText(example.text)}
            className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            {example.label}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Input Text</h3>
          <button
            onClick={handleClear}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          rows={8}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          placeholder="Enter text containing PII to anonymize..."
        />
        <div className="mt-4 flex justify-between items-center">
          <span className="text-sm text-gray-500">
            {inputText.length} characters
          </span>
          <button
            onClick={handleAnonymize}
            disabled={loading || !inputText.trim()}
            className={`
              inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white
              ${
                loading || !inputText.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
              }
            `}
          >
            {loading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Processing...
              </>
            ) : (
              <>
                <svg
                  className="-ml-1 mr-2 h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                    clipRule="evenodd"
                  />
                </svg>
                Anonymize Text
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
              <dt className="text-sm font-medium text-gray-500">Detections</dt>
              <dd className="mt-1 text-3xl font-semibold text-primary-600">
                {result.detections_count}
              </dd>
            </div>
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
              <dt className="text-sm font-medium text-gray-500">Processing Time</dt>
              <dd className="mt-1 text-3xl font-semibold text-primary-600">
                {result.processing_time.toFixed(3)}s
              </dd>
            </div>
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
              <dt className="text-sm font-medium text-gray-500">Mode</dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900 capitalize">
                {mode}
              </dd>
            </div>
          </div>

          {/* Anonymized Text */}
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Anonymized Text
              </h3>
              <button
                onClick={handleCopyResult}
                className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <svg
                  className="-ml-1 mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                  <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                </svg>
                Copy
              </button>
            </div>
            <div className="bg-gray-50 rounded-md p-4 font-mono text-sm whitespace-pre-wrap">
              {result.anonymized_text}
            </div>
          </div>

          {/* Detections List */}
          {result.detections.length > 0 && (
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Detected Entities ({result.detections_count})
              </h3>
              <div className="space-y-2">
                {result.detections.map((detection: Detection, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                  >
                    <div className="flex items-center space-x-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                        {detection.entity_type}
                      </span>
                      <span className="text-sm text-gray-900 font-mono">
                        "{detection.text}"
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {(detection.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TextAnonymization;
