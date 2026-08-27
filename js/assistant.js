/**
 * Lifedrop Assistant - Conversational Agent Logic
 * Follows prompt specifications:
 * - Blood requests with 1-line confirmation
 * - Fast-path for medical emergencies (blood group + location first)
 * - Donor registration
 * - Request status checks
 * - Safe medical boundaries & reassuring answers
 * - Strict anti-hallucination policy
 */

class LifedropAssistant {
  constructor() {
    this.state = {
      currentFlow: null, // 'REQUEST_BLOOD' | 'REGISTER_DONOR' | 'CHECK_STATUS' | null
      step: 0,
      collectedData: {},
      isEmergencyMode: false
    };

    this.bloodGroups = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];
  }

  resetState() {
    this.state = {
      currentFlow: null,
      step: 0,
      collectedData: {},
      isEmergencyMode: false
    };
  }

  /**
   * Main entry point for user text input
   */
  async processMessage(rawInput) {
    const text = (rawInput || '').trim();
    if (!text) {
      return {
        message: "I'm here to help. Would you like to request blood, register as a donor, check a request status, or ask a question?",
        actions: ['Request Blood', 'Register as Donor', 'Check Status', 'Donation FAQs']
      };
    }

    const lower = text.toLowerCase();

    // Check for cancellation/reset keywords
    if (['restart', 'reset', 'cancel', 'start over', 'menu'].includes(lower)) {
      this.resetState();
      return {
        message: "No problem. How can I assist you right now?",
        actions: ['🚨 Urgent Blood Request', '❤️ Register as Donor', '🔍 Check Status', '❓ Blood Donation FAQs']
      };
    }

    // If currently inside an active multi-step flow
    if (this.state.currentFlow) {
      return this.handleActiveFlow(text);
    }

    // Otherwise, parse intent from fresh input
    return this.detectAndStartFlow(text);
  }

  /**
   * Intent Detection
   */
  detectAndStartFlow(text) {
    const lower = text.toLowerCase();

    // 1. Emergency Blood Request
    if (
      lower.includes('emergency') ||
      lower.includes('urgent') ||
      lower.includes('need blood immediately') ||
      lower.includes('critical') ||
      lower.includes('sos') ||
      lower.includes('accident') ||
      lower.includes('icu')
    ) {
      this.state.currentFlow = 'REQUEST_BLOOD';
      this.state.isEmergencyMode = true;
      this.state.collectedData.urgency = 'Emergency';

      // Check if user already provided blood group & location in the first sentence
      const extracted = this.extractDetails(text);
      if (extracted.bloodGroup) this.state.collectedData.bloodGroup = extracted.bloodGroup;
      if (extracted.location) this.state.collectedData.location = extracted.location;

      return this.handleBloodRequestStep(text);
    }

    // 2. Standard Blood Request
    if (
      lower.includes('need blood') ||
      lower.includes('request blood') ||
      lower.includes('find donor') ||
      lower.includes('want blood') ||
      lower.includes('require blood') ||
      lower.includes('looking for donor') ||
      lower.includes('blood required')
    ) {
      this.state.currentFlow = 'REQUEST_BLOOD';
      this.state.isEmergencyMode = false;
      const extracted = this.extractDetails(text);
      if (extracted.bloodGroup) this.state.collectedData.bloodGroup = extracted.bloodGroup;
      if (extracted.location) this.state.collectedData.location = extracted.location;
      if (extracted.urgency) this.state.collectedData.urgency = extracted.urgency;

      return this.handleBloodRequestStep(text);
    }

    // 3. Donor Registration
    if (
      lower.includes('register') ||
      lower.includes('become a donor') ||
      lower.includes('sign up as donor') ||
      lower.includes('want to donate') ||
      lower.includes('volunteer donor') ||
      lower.includes('join as donor')
    ) {
      this.state.currentFlow = 'REGISTER_DONOR';
      this.state.step = 1;
      const extracted = this.extractDetails(text);
      if (extracted.bloodGroup) this.state.collectedData.bloodGroup = extracted.bloodGroup;
      return {
        message: "Thank you for volunteering to save lives. What is your full name?",
        actions: []
      };
    }

    // 4. Request Status Check
    const reqMatch = text.match(/REQ-?\d+/i);
    if (
      lower.includes('status') ||
      lower.includes('track') ||
      lower.includes('check request') ||
      lower.includes('my request') ||
      reqMatch
    ) {
      this.state.currentFlow = 'CHECK_STATUS';
      this.state.step = 1;
      if (reqMatch) {
        return this.handleStatusCheck(reqMatch[0].toUpperCase());
      }
      return {
        message: "Please provide your Request ID (e.g., REQ-1042) or registered phone number to check the current status.",
        actions: ['Check REQ-1042', 'Check REQ-2041']
      };
    }

    // 5. Health & Donor Benefits Knowledge Base (Science, Benefits for Donors, Recovery, Nutrition)
    const healthKnowledge = this.matchHealthAndDonorBenefits(lower);
    if (healthKnowledge) {
      return healthKnowledge;
    }

    // 6. Medical Safety Filter & Advice Boundary Check
    if (this.isMedicalAdviceQuery(lower)) {
      return {
        message: "For your safety and the patient's wellbeing, please consult a certified physician or hospital staff directly regarding medical conditions, medications, or transfusion safety. Would you like to check basic donation eligibility criteria instead?",
        actions: ['Check General Eligibility', 'Call Emergency Hotline (108)', 'Request Blood']
      };
    }

    // 7. Blood Donation FAQs & Knowledge Base
    const faqAnswer = this.matchFAQ(lower);
    if (faqAnswer) {
      return {
        message: faqAnswer,
        actions: ['Request Blood', 'Register as Donor', 'Ask Another Question']
      };
    }

    // 7. Direct Blood Group mention (e.g. "I need O+", "Looking for B+ in Shivamogga")
    const bgFound = this.extractBloodGroup(text);
    if (bgFound) {
      this.state.currentFlow = 'REQUEST_BLOOD';
      this.state.collectedData.bloodGroup = bgFound;
      const loc = this.extractLocation(text);
      if (loc) this.state.collectedData.location = loc;
      return this.handleBloodRequestStep(text);
    }

    // 8. Polite fallback / redirection
    return {
      message: "I am here to help you connect with blood donors and manage donation requests quickly. How may I assist you?",
      actions: [
        '🚨 Urgent Blood Request',
        '❤️ Register as Donor',
        '🔍 Check Request Status',
        '❓ Blood Donation FAQs'
      ]
    };
  }

  /**
   * Active Flow Router
   */
  handleActiveFlow(text) {
    if (this.state.currentFlow === 'REQUEST_BLOOD') {
      return this.handleBloodRequestStep(text);
    }
    if (this.state.currentFlow === 'REGISTER_DONOR') {
      return this.handleDonorRegistrationStep(text);
    }
    if (this.state.currentFlow === 'CHECK_STATUS') {
      return this.handleStatusCheck(text);
    }
    this.resetState();
    return this.detectAndStartFlow(text);
  }

  /**
   * --- FLOW 1: Blood Request Handling ---
   */
  handleBloodRequestStep(text) {
    const data = this.state.collectedData;
    const lower = text.toLowerCase();

    // Check for confirmation answers if we are at confirmation step
    if (this.state.step === 'CONFIRM') {
      if (['yes', 'correct', 'confirm', 'proceed', 'search now', 'yep', 'yeah', 'sure'].some(k => lower.includes(k))) {
        return this.finalizeBloodRequest();
      } else if (['no', 'change', 'edit', 'wrong', 'cancel'].some(k => lower.includes(k))) {
        this.resetState();
        return {
          message: "Let's restart the request. What blood group is needed?",
          actions: ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        };
      }
    }

    // Step 1: Collect Blood Group
    if (!data.bloodGroup) {
      const bg = this.extractBloodGroup(text);
      if (bg) {
        data.bloodGroup = bg;
      } else {
        return {
          message: "Which blood group do you need?",
          actions: ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        };
      }
    }

    // Step 2: Collect Location
    if (!data.location) {
      // Check if location was mentioned in the current text
      const loc = this.extractLocation(text);
      if (loc && loc !== data.bloodGroup) {
        data.location = loc;
      } else if (this.state.step > 0 && text.trim().length > 1) {
        data.location = text.trim();
      } else {
        this.state.step = 2;
        return {
          message: `Got it, ${data.bloodGroup}. What is the city and hospital or area? (e.g., Shivamogga or Bengaluru, Apollo Hospital)`,
          actions: ['Shivamogga', 'Bengaluru', 'Mysuru', 'Hubballi', 'Mumbai']
        };
      }
    }

    // Step 3: Urgency Level
    if (!data.urgency && !this.state.isEmergencyMode) {
      if (lower.includes('immediate') || lower.includes('emergency') || lower.includes('now') || lower.includes('critical')) {
        data.urgency = 'Emergency';
        this.state.isEmergencyMode = true;
      } else if (lower.includes('today') || lower.includes('24') || lower.includes('soon')) {
        data.urgency = 'Within 24 hours';
      } else if (lower.includes('planned') || lower.includes('week') || lower.includes('surgery')) {
        data.urgency = 'Planned (Within 3 days)';
      } else if (this.state.step === 3) {
        data.urgency = text.trim();
      } else {
        this.state.step = 3;
        return {
          message: "What is the urgency level for this request?",
          actions: ['🚨 Immediate / Emergency', '⏰ Within 24 Hours', '📅 Planned (2-3 Days)']
        };
      }
    } else if (!data.urgency && this.state.isEmergencyMode) {
      data.urgency = 'Emergency';
    }

    // Confirmation Step: Strictly in one line as required by prompt
    this.state.step = 'CONFIRM';
    const locName = data.location || 'your area';
    const isEmergency = data.urgency === 'Emergency' || this.state.isEmergencyMode;

    const urgencyPrefix = isEmergency ? "Searching immediately for " : "Searching for ";
    const confirmPrompt = `${urgencyPrefix}${data.bloodGroup} donors near ${locName} — is that correct?`;

    return {
      message: confirmPrompt,
      actions: ['Yes, search now', 'Edit details', 'Cancel']
    };
  }

  finalizeBloodRequest() {
    const data = this.state.collectedData;
    const isEmergency = data.urgency === 'Emergency' || this.state.isEmergencyMode;

    // Save request to storage
    const newReq = window.lifedropStorage.addRequest({
      patientName: data.patientName || 'Emergency Patient',
      bloodGroup: data.bloodGroup,
      units: 1,
      urgency: isEmergency ? 'Emergency' : (data.urgency || 'Standard'),
      city: data.location,
      hospital: data.hospital || data.location,
      contactPhone: data.contactPhone || 'Verified Requester',
      requiredWithin: isEmergency ? 'Immediate' : 'Within 24h'
    });

    // Query matching donors from live backend data
    const matchedDonors = window.lifedropStorage.findDonors({
      bloodGroup: data.bloodGroup,
      city: data.location
    });

    this.resetState();

    if (matchedDonors.length === 0) {
      return {
        message: `Your request (${newReq.id}) has been created for ${data.bloodGroup} in ${data.location}. Currently, no direct online donors are available in ${data.location}. We have alerted our regional blood bank coordinators. You can also dial Emergency Medical Services at 108 or 104.`,
        requestId: newReq.id,
        matchedDonors: [],
        actions: ['View Request Status', 'Call Emergency (108)', 'Find Nearby Blood Banks']
      };
    }

    const donorSummary = matchedDonors.slice(0, 3).map(d => `${d.name} (${d.bloodGroup}, ${d.area})`).join(', ');

    return {
      message: `Request created: ${newReq.id}. We found ${matchedDonors.length} matching verified donor(s) near ${data.location}. Direct alerts have been sent to: ${donorSummary}. You can contact them directly below:`,
      requestId: newReq.id,
      matchedDonors: matchedDonors.slice(0, 3),
      actions: [`Check Status (${newReq.id})`, 'Request Another Unit']
    };
  }

  /**
   * --- FLOW 2: Donor Registration Handling ---
   */
  handleDonorRegistrationStep(text) {
    const data = this.state.collectedData;
    const lower = text.toLowerCase();

    // Confirmation step
    if (this.state.step === 'CONFIRM') {
      if (['yes', 'correct', 'confirm', 'proceed', 'submit', 'yep', 'sure'].some(k => lower.includes(k))) {
        const newDonor = window.lifedropStorage.addDonor({
          name: data.name,
          bloodGroup: data.bloodGroup,
          city: data.city,
          area: data.area || data.city,
          phone: data.phone,
          isEmergencyContact: true
        });

        this.resetState();
        return {
          message: `Thank you, ${newDonor.name}! You are now registered as an active ${newDonor.bloodGroup} donor in ${newDonor.city}. Your Donor ID is ${newDonor.id}. Your willingness to donate will save lives.`,
          donor: newDonor,
          actions: ['View My Donor Card', 'View Live Blood Requests']
        };
      } else {
        this.resetState();
        return {
          message: "Registration cancelled. Let me know if you would like to start over or do something else.",
          actions: ['Register as Donor', 'Request Blood']
        };
      }
    }

    // Step 1: Collect Name
    if (!data.name) {
      if (this.state.step === 1 && text.trim().length > 1) {
        data.name = text.trim();
      } else {
        this.state.step = 1;
        return {
          message: "Thank you for stepping forward. What is your full name?",
          actions: []
        };
      }
    }

    // Step 2: Collect Blood Group
    if (!data.bloodGroup) {
      const bg = this.extractBloodGroup(text);
      if (bg) {
        data.bloodGroup = bg;
      } else {
        this.state.step = 2;
        return {
          message: `Hello ${data.name}! What is your blood group?`,
          actions: ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        };
      }
    }

    // Step 3: Collect City/Location
    if (!data.city) {
      if (this.state.step === 3 && text.trim().length > 1) {
        data.city = text.trim();
        data.area = text.trim();
      } else {
        this.state.step = 3;
        return {
          message: `Great. Which city and area are you located in? (e.g., Shivamogga, Vidyanagar)`,
          actions: ['Shivamogga', 'Bengaluru', 'Mysuru', 'Hubballi', 'Mumbai']
        };
      }
    }

    // Step 4: Collect Contact Phone Number
    if (!data.phone) {
      const phoneMatch = text.match(/(\+?\d[\d -]{8,13}\d)/);
      if (phoneMatch) {
        data.phone = phoneMatch[0].trim();
      } else if (this.state.step === 4 && text.replace(/\D/g, '').length >= 10) {
        data.phone = text.trim();
      } else {
        this.state.step = 4;
        return {
          message: `Almost done. Please provide your contact phone number so coordinators can reach you for donations.`,
          actions: []
        };
      }
    }

    // Step 5: Confirmation before finalizing
    this.state.step = 'CONFIRM';
    return {
      message: `Please confirm your donor registration:\n• Name: ${data.name}\n• Blood Group: ${data.bloodGroup}\n• Location: ${data.city}\n• Contact: ${data.phone}\n\nIs this information correct?`,
      actions: ['Yes, register me', 'Cancel']
    };
  }

  /**
   * --- FLOW 3: Request Status Lookup ---
   */
  handleStatusCheck(query) {
    const clean = query.replace(/check\s+/i, '').trim();
    const req = window.lifedropStorage.getRequestById(clean);

    this.resetState();

    if (!req) {
      return {
        message: `I couldn't find an active blood request with ID or phone "${clean}". Please double-check the ID (e.g., REQ-1042) or create a new request.`,
        actions: ['Check REQ-1042', 'Check REQ-2041', 'Create Blood Request']
      };
    }

    const latestUpdate = req.timeline && req.timeline.length > 0 
      ? req.timeline[req.timeline.length - 1].event 
      : 'Active';

    return {
      message: `Request ${req.id} Status:\n• Patient/Case: ${req.patientName}\n• Blood Group: ${req.bloodGroup} (${req.units} units)\n• Location: ${req.hospital}, ${req.city}\n• Current Status: ${req.status}\n• Latest Update: ${latestUpdate}\n• Confirmed Donors: ${req.donorsConfirmed} / ${req.donorsContacted} alerted.`,
      request: req,
      actions: ['Track on Live Map', 'Request More Donors', 'Done']
    };
  }

  /**
   * Health & Donor Benefits Knowledge Engine
   */
  matchHealthAndDonorBenefits(lower) {
    // 1. Health benefits for the donor
    if ([
      'how help donor', 'how helps donor', 'benefit of blood donation', 'benefits of donating',
      'benefit of donating', 'benefits for donor', 'benefit for donor', 'why donate blood',
      'why should i donate', 'advantages of donating', 'what do i get', 'does donating blood help',
      'good for health', 'helps donor', 'healthy for donor', 'donor health benefit',
      'what are the benefits', 'why give blood', 'impact on donor', 'help the donor', 'advantage for donor'
    ].some(p => lower.includes(p)) && !lower.includes('receive from')) {
      return {
        message: "🩺 **How Blood Donation Helps the Donor (Key Health Benefits)**:\n\n1. **Free Comprehensive Mini-Health Screening**:\n   • Every donation includes blood pressure, pulse rate, temperature, and hemoglobin tests, plus screening for infectious diseases (HIV, Hep B/C, Syphilis, Malaria).\n\n2. **Stimulates Fresh Blood Cell Production (Erythropoiesis)**:\n   • Bone marrow is activated to generate fresh red blood cells, immune white cells, and platelets, enhancing oxygen delivery.\n\n3. **Cardiovascular & Blood Flow Health**:\n   • Lowers blood viscosity (thickness), reducing arterial friction and oxidative stress on blood vessel walls.\n\n4. **Balances Iron Stores & Prevents Iron Overload**:\n   • Eliminates excess toxic iron deposits, protecting arteries, liver, and heart.\n\n5. **Caloric Expenditure & Metabolism**:\n   • The body burns approximately **650 calories** synthesizing and replenishing 1 pint (450ml) of donated blood volume.\n\n6. **Psychological 'Warm Glow' & Mental Wellbeing**:\n   • Altruistic giving releases endorphins and reduces stress—every donation can **save up to 3 lives**! ❤️",
        actions: ['❤️ Register as Donor', '🩸 Check Inventory', '❓ Eligibility Criteria', '🥗 Nutrition Tips']
      };
    }

    // 2. Biological Cell Renewal
    if (['bone marrow', 'cell renewal', 'how body makes blood', 'erythropoiesis', 'new blood cell', 'replenish', 'grow back', 'blood regeneration', 'how fast does blood'].some(k => lower.includes(k))) {
      return {
        message: "🔬 **How Your Body Replenishes Blood (Biological Renewal Timeline)**:\n\n• **Plasma / Fluid Volume (24–48 Hours)**: Restored within 1–2 days with healthy hydration.\n• **Platelets & White Blood Cells (72 Hours)**: Clotting platelets recover rapidly within 3 days.\n• **Red Blood Cells (4–6 Weeks)**: Bone marrow produces millions of fresh RBCs stimulated by erythropoietin.\n• **Iron Stores (8–12 Weeks)**: Ferritin/iron stores replenish over 8–12 weeks.",
        actions: ['Donor Health Benefits', '🥗 Nutrition Tips', '❤️ Register as Donor']
      };
    }

    // 3. Nutrition & Hemoglobin
    if (['increase hemoglobin', 'raise hemoglobin', 'low hemoglobin', 'iron rich', 'what to eat', 'diet for donor', 'food before', 'food after', 'nutrition', 'vitamin c', 'boost hb'].some(k => lower.includes(k))) {
      return {
        message: "🥗 **Nutrition & Hemoglobin Guide for Donors**:\n\n• **Iron-Rich Foods**: Spinach, kale, lentils, chickpeas, beetroot, pomegranate, dates, jaggery, and eggs.\n• **Vitamin C Multiplier**: Pairing iron with Vitamin C (oranges, amla, lemons, tomatoes) boosts iron absorption by up to **300%**.\n• **Avoid with Meals**: Tea and coffee inhibit iron absorption.\n• **Pre-Donation**: Drink 500ml water, eat 2–3 hours prior, and avoid alcohol for 24h.",
        actions: ['Donor Health Benefits', '❓ Eligibility Criteria', '❤️ Register as Donor']
      };
    }

    // 4. Blood Components & Donation Types
    if (['blood component', 'platelet donation', 'plasma donation', 'apheresis', 'what is plasma', 'what are platelet', 'cryoprecipitate', 'sdp'].some(k => lower.includes(k))) {
      return {
        message: "🩸 **Blood Components & Specialized Donation Types**:\n\n1. **Whole Blood**: Standard 450ml donation separated into RBCs, platelets, and plasma (every 90/120 days).\n2. **Platelet Donation (Apheresis / SDP)**: Critical for cancer, leukemia, and dengue patients. Can donate **every 15 days** (up to 24 times/year)!\n3. **Plasma (FFP)**: Rich in antibodies and clotting factors; essential for burn, trauma, and shock victims.\n4. **Packed Red Cells (PRBC)**: Concentrated red cells for acute anemia and surgeries.",
        actions: ['Find Platelet Donors', '🩸 Check Inventory', '🚨 Urgent Blood Request']
      };
    }

    // 5. Common Medical Conditions
    if (['blood pressure', 'hypertension', 'diabetes', 'diabetic', 'thyroid', 'tattoo', 'alcohol', 'smoking', 'smoker', 'piercing', 'vaccine'].some(k => lower.includes(k))) {
      return {
        message: "📋 **Health Conditions & Blood Donation Eligibility**:\n\n• **Blood Pressure**: Eligible if BP is between 90/50 and 180/100 mmHg on donation day.\n• **Diabetes**: Eligible if blood sugar is well-controlled via diet or oral medication.\n• **Thyroid**: Eligible if on stable hormone replacement (e.g. Levothyroxine) and asymptomatic.\n• **Tattoos & Piercings**: Eligible **6 months** after getting inked at a licensed studio.\n• **Alcohol / Smoking**: Avoid alcohol 24h prior; avoid smoking 2h before & after donation.",
        actions: ['❓ Eligibility Criteria', 'Donor Health Benefits', '❤️ Register as Donor']
      };
    }

    return null;
  }

  /**
   * Medical Advice Safety Filter
   */
  isMedicalAdviceQuery(lower) {
    const medicalKeywords = [
      'hiv', 'hepatitis', 'cancer', 'chemotherapy', 'diabetes insulin',
      'can i donate if i have', 'is it safe for patient', 'transfusion reaction',
      'blood mismatch risk', 'heart disease', 'pregnancy', 'pregnant', 'abortion',
      'surgery recently', 'antibiotics', 'medicine'
    ];
    return medicalKeywords.some(k => lower.includes(k));
  }

  /**
   * FAQ Matcher
   */
  matchFAQ(lower) {
    if (lower.includes('who can donate') || lower.includes('eligible') || lower.includes('age limit') || lower.includes('weight')) {
      return "Eligibility criteria: Age 18–65 years, weight at least 50 kg, hemoglobin > 12.5 g/dL, and feeling healthy with no recent illness.";
    }
    if (lower.includes('how often') || lower.includes('interval') || lower.includes('frequency') || lower.includes('gap')) {
      return "Whole blood can be donated every 90 days (3 months) for men and every 120 days (4 months) for women to allow iron stores to recover.";
    }
    if (lower.includes('safe') || lower.includes('risk') || lower.includes('infection') || lower.includes('pain')) {
      return "Donating blood is 100% safe. Single-use, sterile, disposable needles are used for every donor. The body replenishes the donated fluid volume within 24–48 hours.";
    }
    if (lower.includes('before') || lower.includes('after') || lower.includes('prepare') || lower.includes('eat') || lower.includes('food')) {
      return "Drink 500ml of water, eat a healthy meal 2-3 hours prior, and avoid alcohol for 24 hours. After donation, rest for 15 minutes, hydrate well, and avoid strenuous exercise for the day.";
    }
    if (lower.includes('universal') || lower.includes('o-') || lower.includes('o negative')) {
      return "O- negative is the Universal Red Blood Cell Donor. It can be safely transfused to patients of any blood group during life-threatening trauma emergencies.";
    }
    return null;
  }

  /**
   * Helper extractors
   */
  extractBloodGroup(text) {
    const upper = text.toUpperCase();
    const match = upper.match(/\b(O\+|O\-|A\+|A\-|B\+|B\-|AB\+|AB\-)\b/);
    if (match) return match[1];

    if (/O\s*POSITIVE/i.test(text)) return 'O+';
    if (/O\s*NEGATIVE/i.test(text)) return 'O-';
    if (/A\s*POSITIVE/i.test(text)) return 'A+';
    if (/A\s*NEGATIVE/i.test(text)) return 'A-';
    if (/B\s*POSITIVE/i.test(text)) return 'B+';
    if (/B\s*NEGATIVE/i.test(text)) return 'B-';
    if (/AB\s*POSITIVE/i.test(text)) return 'AB+';
    if (/AB\s*NEGATIVE/i.test(text)) return 'AB-';
    return null;
  }

  extractLocation(text) {
    const knownCities = [
      'Shivamogga', 'Shimoga', 'Durgigudi', 'Gopala', 'Vinoba Nagara', 'Vinoba Nagar',
      'Gandhi Nagara', 'Gandhi Nagar', 'Tilak Nagara', 'Tilak Nagar', 'Vidyanagara', 'Vidyanagar',
      'Kuvempu Road', 'Savalanga Road', 'Savalanga', 'Purle', 'Harakere', 'Alkola', 'Jayanagara',
      'NT Road', 'Jail Road', 'Sagara', 'Sagar', 'Bhadravathi', 'Bhadravati', 'Thirthahalli',
      'Tirthahalli', 'Shikaripura', 'Shikaripur', 'Soraba', 'Sorab', 'Hosanagara', 'Hosanagar',
      'McGann', 'SIMS', 'Sahyadri', 'Nanjappa', 'Subbaiah', 'Rotary', 'Max Hospital',
      'District Hospital', 'KIMS', 'Bengaluru', 'Mumbai', 'Pune', 'Mysuru', 'Mangaluru', 'Chennai'
    ];
    for (const city of knownCities) {
      if (new RegExp(`\\b${city}\\b`, 'i').test(text)) {
        return city;
      }
    }
    return null;
  }

  extractDetails(text) {
    return {
      bloodGroup: this.extractBloodGroup(text),
      location: this.extractLocation(text),
      urgency: /emergency|immediate|urgent|critical/i.test(text) ? 'Emergency' : null
    };
  }

  processUserInput(rawInput) {
    const res = this.processMessage(rawInput);
    if (res && typeof res.then === 'function') {
      return res;
    }
    if (res && res.actions && !res.quickReplies) {
      res.quickReplies = res.actions;
    }
    return res;
  }
}

// Global instance
window.lifedropAssistant = new LifedropAssistant();

