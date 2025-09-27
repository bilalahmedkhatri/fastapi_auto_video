'use client';

export default function Support() {
  const faqs = [
    {
      question: 'How do I create a new video project?',
      answer: 'Navigate to the Projects page and click "Create New Project". Follow the wizard to set up your video parameters and start generating content.'
    },
    {
      question: 'Can I customize the AI-generated scripts?',
      answer: 'Yes! After the AI generates a script, you can edit, modify, and customize it to match your requirements before creating the video.'
    },
    {
      question: 'What video formats are supported?',
      answer: 'We support MP4, MOV, AVI, and WebM formats for both input and output videos.'
    },
    {
      question: 'How do I share my videos with team members?',
      answer: 'Go to the Users page and invite team members. You can set different permission levels for viewing, editing, or managing projects.'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Support</h1>
        <p className="text-gray-600 dark:text-gray-300 mt-2">Get help and find answers to common questions</p>
      </div>

      {/* Contact Support */}
      <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Contact Support</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-2">📧</div>
            <h3 className="font-medium text-gray-900 dark:text-white">Email Support</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">support@untitledui.com</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Response within 24 hours</p>
          </div>
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-2">💬</div>
            <h3 className="font-medium text-gray-900 dark:text-white">Live Chat</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">Available 9 AM - 6 PM EST</p>
            <button className="mt-2 text-xs bg-indigo-600 text-white px-3 py-1 rounded-lg hover:bg-indigo-700 transition-colors">
              Start Chat
            </button>
          </div>
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-2xl mb-2">📚</div>
            <h3 className="font-medium text-gray-900 dark:text-white">Documentation</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">Comprehensive guides</p>
            <button className="mt-2 text-xs bg-indigo-600 text-white px-3 py-1 rounded-lg hover:bg-indigo-700 transition-colors">
              View Docs
            </button>
          </div>
        </div>
      </div>

      {/* FAQs */}
      <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-6">Frequently Asked Questions</h2>
        <div className="space-y-6">
          {faqs.map((faq, index) => (
            <div key={index} className="border-b border-gray-200 dark:border-gray-700 last:border-b-0 pb-6 last:pb-0">
              <h3 className="text-medium font-medium text-gray-900 dark:text-white mb-2">
                {faq.question}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                {faq.answer}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
