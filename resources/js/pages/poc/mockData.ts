export interface Appointment {
    id: string;
    title: string;
    start: string; // ISO string e.g. "2026-09-11T09:00:00"
    end: string;
    branchId: 'b1' | 'b2' | 'b3';
    patientName: string;
    patientPhone: string;
    doctorName: string;
    treatment: string;
    price: number;
    status: 'pending_bill' | 'confirmed' | 'paid';
    notes?: string;
}

export interface Branch {
    id: 'b1' | 'b2' | 'b3';
    name: string;
    address: string;
    color: string;
    badgeClass: string;
}

export interface Doctor {
    id: string;
    name: string;
    specialty: string;
}

export const clinicBranches: Branch[] = [
    {
        id: 'b1',
        name: 'สาขา สยามสแควร์ (Siam Square)',
        address: 'อาคารสยามสแควร์วัน ชั้น 4',
        color: '#3b82f6',
        badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-200 dark:border-blue-800'
    },
    {
        id: 'b2',
        name: 'สาขา อารีย์ (Ari)',
        address: 'พหลโยธินซอย 7 อาคารลาวิลล่า',
        color: '#10b981',
        badgeClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
    },
    {
        id: 'b3',
        name: 'สาขา ทองหล่อ (Thong Lo)',
        address: 'สุขุมวิท 55 ทองหล่อซอย 10',
        color: '#8b5cf6',
        badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border-purple-200 dark:border-purple-800'
    }
];

export const clinicDoctors: Doctor[] = [
    { id: 'd1', name: 'ทพ. ภัทร วาจาสัตย์', specialty: 'ทันตกรรมทั่วไป & ขูดหินปูน' },
    { id: 'd2', name: 'ทพญ. นภัสสร ศิริมงคล', specialty: 'จัดฟัน & ทันตกรรมเพื่อความงาม' },
    { id: 'd3', name: 'ทพ. ธนกฤต มั่นคง', specialty: 'ศัลยกรรมช่องปาก & รากฟันเทียม' }
];

export const treatmentOptions = [
    { name: 'ขูดหินปูน & ขัดฟัน (Scaling)', price: 900 },
    { name: 'อุดฟันคอมโพสิต (Composite Filling)', price: 1500 },
    { name: 'ฟอกสีฟัน Cool Light (Whitening)', price: 4900 },
    { name: 'จัดฟันใส Invisalign (Consultation)', price: 3500 },
    { name: 'ผ่าฟันคุด (Wisdom Tooth Surgery)', price: 2800 },
    { name: 'รักษารากฟัน (Root Canal Treatment)', price: 6500 }
];

/**
 * Generate initial realistic appointments around the current date
 */
export function getInitialAppointments(): Appointment[] {
    const now = new Date();
    // Helper to get formatted date string for an offset from today
    const getOffsetDate = (offsetDays: number) => {
        const d = new Date(now);
        d.setDate(d.getDate() + offsetDays);
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    };

    // Current week dates: Sunday to Saturday
    const currentDay = now.getDay(); // 0 = Sun, 1 = Mon, ..., 3 = Wed
    const monStr = getOffsetDate(1 - currentDay);
    const tueStr = getOffsetDate(2 - currentDay);
    const wedStr = getOffsetDate(3 - currentDay);
    const thuStr = getOffsetDate(4 - currentDay);
    const friStr = getOffsetDate(5 - currentDay);
    const satStr = getOffsetDate(6 - currentDay);

    return [
        // --- วันจันทร์ (Monday) ---
        {
            id: 'apt-mon-1',
            title: 'ขูดหินปูน & ขัดฟัน',
            start: `${monStr}T09:00:00`,
            end: `${monStr}T10:00:00`,
            branchId: 'b1',
            patientName: 'นาย สมชาย ใจดี',
            patientPhone: '081-234-5678',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'ขูดหินปูน & ขัดฟัน (Scaling)',
            price: 900,
            status: 'paid',
            notes: 'คนไข้ประจำ ตรวจฟันประจำปี'
        },
        {
            id: 'apt-mon-2',
            title: 'ผ่าฟันคุด กรามล่างขวา',
            start: `${monStr}T13:30:00`,
            end: `${monStr}T15:00:00`,
            branchId: 'b2',
            patientName: 'นางสาว ณิชา เจริญสุข',
            patientPhone: '082-456-7890',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'ผ่าฟันคุด (Wisdom Tooth Surgery)',
            price: 2800,
            status: 'paid',
            notes: 'นัดตัดไหมสัปดาห์หน้า'
        },

        // --- วันอังคาร (Tuesday) ---
        {
            id: 'apt-tue-1',
            title: 'รักษารากฟัน ครั้งที่ 1',
            start: `${tueStr}T10:00:00`,
            end: `${tueStr}T11:30:00`,
            branchId: 'b3',
            patientName: 'คุณ วิภาดา ศรีสวัสดิ์',
            patientPhone: '083-999-0011',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'รักษารากฟัน (Root Canal Treatment)',
            price: 6500,
            status: 'pending_bill'
        },
        {
            id: 'apt-tue-2',
            title: 'ฟอกสีฟัน Cool Light',
            start: `${tueStr}T14:00:00`,
            end: `${tueStr}T15:30:00`,
            branchId: 'b1',
            patientName: 'นาย กิตติศักดิ์ พรหมดี',
            patientPhone: '085-111-2233',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'ฟอกสีฟัน Cool Light (Whitening)',
            price: 4900,
            status: 'pending_bill'
        },

        // --- วันพุธ (Wednesday - วันนี้) ---
        // เคสตัวอย่างที่ 1 (ช่วงเช้า 09:30 - 11:00): หมอ 2 ท่านทำหัตถการในเวลาเดียวกันตรงเป๊ะ
        {
            id: 'apt-wed-1',
            title: 'จัดฟันใส Invisalign Follow-up',
            start: `${wedStr}T09:30:00`,
            end: `${wedStr}T11:00:00`,
            branchId: 'b1',
            patientName: 'นางสาว แพรวา วงศ์สว่าง',
            patientPhone: '089-876-5432',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'จัดฟันใส Invisalign (Consultation)',
            price: 3500,
            status: 'confirmed',
            notes: 'รับถาด Invisalign ชุดที่ 8'
        },
        {
            id: 'apt-wed-concurrent-am',
            title: 'ผ่าฟันคุด กรามล่างขวา',
            start: `${wedStr}T09:30:00`,
            end: `${wedStr}T11:00:00`,
            branchId: 'b2',
            patientName: 'นาย อนันต์ ทวีทรัพย์',
            patientPhone: '081-777-6655',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'ผ่าฟันคุด (Wisdom Tooth Surgery)',
            price: 2800,
            status: 'pending_bill',
            notes: 'เคสฉุกเฉิน นัดผ่าฟันคุดพร้อมกันช่วงเช้า'
        },

        // เคสตัวอย่างที่ 2 (ช่วงบ่าย 14:00 - 15:30): หมอ 2 ท่านทำหัตถการในเวลาเดียวกัน
        {
            id: 'apt-wed-2',
            title: 'ขูดหินปูน & ขัดฟัน',
            start: `${wedStr}T14:00:00`,
            end: `${wedStr}T15:30:00`,
            branchId: 'b3',
            patientName: 'นาย สิทธิชัย วัฒนานนท์',
            patientPhone: '084-222-3344',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'ขูดหินปูน & ขัดฟัน (Scaling)',
            price: 900,
            status: 'paid'
        },
        {
            id: 'apt-wed-concurrent-pm',
            title: 'อุดฟันคอมโพสิต 2 ซี่',
            start: `${wedStr}T14:00:00`,
            end: `${wedStr}T15:30:00`,
            branchId: 'b1',
            patientName: 'นาย ธนพล รัตนโกสินทร์',
            patientPhone: '086-777-8899',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'อุดฟันคอมโพสิต (Composite Filling)',
            price: 3000,
            status: 'pending_bill'
        },
        {
            id: 'apt-wed-4',
            title: 'ฟอกสีฟัน Cool Light',
            start: `${wedStr}T16:30:00`,
            end: `${wedStr}T17:45:00`,
            branchId: 'b1',
            patientName: 'นางสาว พัชรากร สินธุ',
            patientPhone: '081-555-4321',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'ฟอกสีฟัน Cool Light (Whitening)',
            price: 4900,
            status: 'paid',
            notes: 'ตรวจติดตามหลังฟอกสีฟัน 6 เดือน'
        },

        // --- วันพฤหัสบดี (Thursday) ---
        {
            id: 'apt-thu-1',
            title: 'จัดฟันใส เช็กความคืบหน้า',
            start: `${thuStr}T10:30:00`,
            end: `${thuStr}T11:30:00`,
            branchId: 'b1',
            patientName: 'นาย พงศกร มหัทธนะ',
            patientPhone: '081-999-8888',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'จัดฟันใส Invisalign (Consultation)',
            price: 3500,
            status: 'confirmed'
        },
        {
            id: 'apt-thu-2',
            title: 'ตรวจสุขภาพฟัน & X-Ray',
            start: `${thuStr}T13:30:00`,
            end: `${thuStr}T14:30:00`,
            branchId: 'b2',
            patientName: 'นางสาว วรรณภา มณีรัตน์',
            patientPhone: '089-333-4455',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'ตรวจสุขภาพช่องปาก & ถ่ายภาพรังสี',
            price: 1200,
            status: 'pending_bill'
        },

        // --- วันศุกร์ (Friday) ---
        {
            id: 'apt-fri-1',
            title: 'รักษารากฟัน ครั้งที่ 2',
            start: `${friStr}T09:30:00`,
            end: `${friStr}T11:00:00`,
            branchId: 'b3',
            patientName: 'นาย จิรายุ เด่นชัย',
            patientPhone: '087-555-6677',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'รักษารากฟัน (Root Canal Treatment)',
            price: 6500,
            status: 'pending_bill'
        },
        {
            id: 'apt-fri-2',
            title: 'อุดฟันคอมโพสิต',
            start: `${friStr}T13:00:00`,
            end: `${friStr}T14:15:00`,
            branchId: 'b1',
            patientName: 'นางสาว กมลชนก สุขใจ',
            patientPhone: '088-123-9988',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'อุดฟันคอมโพสิต (Composite Filling)',
            price: 1500,
            status: 'paid'
        },

        // --- วันเสาร์ (Saturday) ---
        {
            id: 'apt-sat-1',
            title: 'จัดฟันใส Invisalign Consultation',
            start: `${satStr}T09:30:00`,
            end: `${satStr}T11:00:00`,
            branchId: 'b1',
            patientName: 'นางสาว ธนัญญา โชคอนันต์',
            patientPhone: '082-888-9900',
            doctorName: 'ทพญ. นภัสสร ศิริมงคล',
            treatment: 'จัดฟันใส Invisalign (Consultation)',
            price: 5000,
            status: 'pending_bill'
        },
        {
            id: 'apt-sat-2',
            title: 'ฟอกสีฟัน Cool Light',
            start: `${satStr}T11:30:00`,
            end: `${satStr}T13:00:00`,
            branchId: 'b3',
            patientName: 'นาย อนุพงศ์ ชัยชนะ',
            patientPhone: '081-444-5566',
            doctorName: 'ทพ. ภัทร วาจาสัตย์',
            treatment: 'ฟอกสีฟัน Cool Light (Whitening)',
            price: 4900,
            status: 'confirmed'
        },
        {
            id: 'apt-sat-3',
            title: 'ผ่าฟันคุด กรามบนซ้าย',
            start: `${satStr}T14:00:00`,
            end: `${satStr}T15:30:00`,
            branchId: 'b2',
            patientName: 'นาย วรภัทร สุขสมบัติ',
            patientPhone: '083-666-7788',
            doctorName: 'ทพ. ธนกฤต มั่นคง',
            treatment: 'ผ่าฟันคุด (Wisdom Tooth Surgery)',
            price: 2800,
            status: 'pending_bill'
        }
    ];
}
