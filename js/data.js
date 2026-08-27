/**
 * Lifedrop - Seed Data & Medical Compatibility Rules
 */

const LIFEDROP_DATA = {
  // Blood compatibility data (Red Blood Cells)
  compatibility: {
    'O-': {
      canDonateTo: ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
      canReceiveFrom: ['O-'],
      badge: 'Universal Red Cell Donor',
      description: 'O- can be given to anyone in emergency situations when blood type is unknown.'
    },
    'O+': {
      canDonateTo: ['O+', 'A+', 'B+', 'AB+'],
      canReceiveFrom: ['O+', 'O-'],
      badge: 'Most Common Blood Type',
      description: 'Can give to all positive blood types. High in demand across emergency rooms.'
    },
    'A-': {
      canDonateTo: ['A-', 'A+', 'AB-', 'AB+'],
      canReceiveFrom: ['A-', 'O-'],
      badge: 'Crucial for A & AB Patients',
      description: 'Can donate to all A and AB types regardless of Rh factor.'
    },
    'A+': {
      canDonateTo: ['A+', 'AB+'],
      canReceiveFrom: ['A+', 'A-', 'O+', 'O-'],
      badge: 'High Demand Blood Type',
      description: 'Second most common blood type, needed for cancer treatments and surgeries.'
    },
    'B-': {
      canDonateTo: ['B-', 'B+', 'AB-', 'AB+'],
      canReceiveFrom: ['B-', 'O-'],
      badge: 'Rare Blood Type',
      description: 'Only about 2% of the population has B-, making every donor vital.'
    },
    'B+': {
      canDonateTo: ['B+', 'AB+'],
      canReceiveFrom: ['B+', 'B-', 'O+', 'O-'],
      badge: 'Widely Needed',
      description: 'Can donate red blood cells to B+ and AB+ recipients.'
    },
    'AB-': {
      canDonateTo: ['AB-', 'AB+'],
      canReceiveFrom: ['AB-', 'A-', 'B-', 'O-'],
      badge: 'Rarest Blood Type',
      description: 'Less than 1% of population. Universal plasma donor.'
    },
    'AB+': {
      canDonateTo: ['AB+'],
      canReceiveFrom: ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
      badge: 'Universal Red Cell Recipient',
      description: 'Can safely receive red blood cells from any blood group.'
    }
  },

  // Verified initial donors (empty initially for live user registrations)
  donors: [],

  // Live Urgent & Active Blood Requests (empty initially for live patient requests)
  requests: [],

  // Knowledge base FAQs & medical boundaries
  faqs: [
    {
      q: 'Who is eligible to donate blood?',
      a: 'Healthy individuals aged 18–65 years, weighing at least 50 kg (110 lbs), with normal hemoglobin (above 12.5 g/dL), and feeling generally well on donation day.',
      category: 'eligibility'
    },
    {
      q: 'How often can I donate blood?',
      a: 'Whole blood can safely be donated every 90 days (3 months) for men and every 120 days (4 months) for women, giving your body ample time to replenish iron stores.',
      category: 'frequency'
    },
    {
      q: 'What should I do before and after donating?',
      a: 'Drink plenty of water (500ml), eat a nutritious light meal 2-3 hours prior, and avoid alcohol for 24 hours. After donating, rest for 10-15 minutes, hydrate, and avoid heavy lifting for the rest of the day.',
      category: 'preparation'
    },
    {
      q: 'Is donating blood safe?',
      a: 'Yes, completely safe. A sterile, disposable needle and bag set is used for every single donor and disposed of immediately. You cannot contract any infection from donating blood.',
      category: 'safety'
    },
    {
      q: 'Why is O- negative so important?',
      a: 'O negative blood cells can be safely given to recipients of ANY blood group. It is the first blood used in trauma centers and emergencies when patient blood typing cannot wait.',
      category: 'blood-types'
    }
  ],

  // Blood Bank Inventory Live Status (Shivamogga District Center)
  inventory: [
    { bloodGroup: 'O+', unitsAvailable: 86, dailyDemand: 28, status: 'Stable', capacityPct: 75 },
    { bloodGroup: 'O-', unitsAvailable: 12, dailyDemand: 22, status: 'Critical', capacityPct: 20 },
    { bloodGroup: 'A+', unitsAvailable: 64, dailyDemand: 18, status: 'Stable', capacityPct: 68 },
    { bloodGroup: 'A-', unitsAvailable: 14, dailyDemand: 11, status: 'Low', capacityPct: 35 },
    { bloodGroup: 'B+', unitsAvailable: 78, dailyDemand: 24, status: 'Stable', capacityPct: 80 },
    { bloodGroup: 'B-', unitsAvailable: 9, dailyDemand: 8, status: 'Critical', capacityPct: 18 },
    { bloodGroup: 'AB+', unitsAvailable: 38, dailyDemand: 9, status: 'Stable', capacityPct: 65 },
    { bloodGroup: 'AB-', unitsAvailable: 5, dailyDemand: 6, status: 'Critical', capacityPct: 15 }
  ],

  // Shivamogga Emergency Helplines & Blood Banks
  helplines: [
    { name: 'McGann Teaching Hospital & SIMS Blood Bank', number: '08182-222233' },
    { name: 'District Government Hospital Shivamogga', number: '08182-222444' },
    { name: 'Sahyadri Narayana Hospital Blood Centre', number: '08182-244555' },
    { name: 'Rotary Blood Bank Shivamogga (Durgigudi)', number: '08182-277888' },
    { name: 'Indian Red Cross Society Shivamogga', number: '08182-225678' },
    { name: 'Karnataka Emergency Medical Ambulance', number: '108' }
  ]
};

// Expose globally
window.LIFEDROP_DATA = LIFEDROP_DATA;
