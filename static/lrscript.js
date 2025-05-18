const translations = {
    en: {
        "page-title": "Laborer Registration",
        "language-label": "Switch Language:",
        "form-title": "Laborer Registration",
        "label-name": "Name:",
        "label-phone": "Phone No:",
        "label-language": "Preferred Language:",
        "label-aadhar": "Aadhar No.:",
        "label-dob": "Date of Birth:",
        "label-sex": "Sex:",
        "label-male": "Male",
        "label-female": "Female",
        "label-address": "Address:",
        "label-abilities": "Abilities:",
        "ability-construction": "Construction",
        "ability-plumbing": "Plumbing",
        "ability-electrician": "Electrician",
        "ability-carpentry": "Carpentry",
        "ability-painting": "Painting",
        "ability-gardening": "Gardening",
        "ability-welding": "Welding",
        "ability-masonry": "Masonry",
        "ability-mechanic": "Mechanic",
        "ability-factory-worker": "Factory Worker",
        "label-employment-length": "Preferred Length of Employment:",
        "employment-days": "Days",
        "employment-months": "Months",
        "label-photo": "Upload Photo:",
        "label-employment-proof": "Proof of Past Employment:",
        "submit-btn": "Register"
    },
    hindi: {
        "page-title": "श्रमिक पंजीकरण",
        "language-label": "भाषा बदलें:",
        "form-title": "श्रमिक पंजीकरण",
        "label-name": "नाम:",
        "label-phone": "फोन नंबर:",
        "label-language": "पसंदीदा भाषा:",
        "label-aadhar": "आधार नंबर:",
        "label-dob": "जन्म तिथि:",
        "label-sex": "लिंग:",
        "label-male": "पुरुष",
        "label-female": "महिला",
        "label-address": "पता:",
        "label-abilities": "कौशल:",
        "ability-construction": "निर्माण",
        "ability-plumbing": "प्लंबिंग",
        "ability-electrician": "बिजली मिस्त्री",
        "ability-carpentry": "बढ़ईगीरी",
        "ability-painting": "पेंटिंग",
        "ability-gardening": "बागवानी",
        "ability-welding": "वेल्डिंग",
        "ability-masonry": "राजमिस्त्री",
        "ability-mechanic": "मेकैनिक",
        "ability-factory-worker": "कारखाना कर्मचारी",
        "label-employment-length": "नौकरी की पसंदीदा अवधि:",
        "employment-days": "दिन",
        "employment-months": "महीने",
        "label-photo": "फोटो अपलोड करें:",
        "label-employment-proof": "पिछले रोजगार का प्रमाण:",
        "submit-btn": "पंजीकरण करें"
    }
};

document.getElementById("language-switch").addEventListener("change", function() {
    const selectedLang = this.value;
    document.querySelectorAll("[id]").forEach(el => {
        if (translations[selectedLang][el.id]) {
            el.innerText = translations[selectedLang][el.id];
        }
    });
    
    document.querySelectorAll("#abilities option").forEach(option => {
        if (translations[selectedLang][option.id]) {
            option.innerText = translations[selectedLang][option.id];
        }
    });
    
    document.querySelectorAll("#employment-unit option").forEach(option => {
        if (translations[selectedLang][option.id]) {
            option.innerText = translations[selectedLang][option.id];
        }
    });
});
