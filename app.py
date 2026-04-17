<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>연차 관리 대시보드</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    
    <style>
        .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background-color: #cbd5e1;
            border-radius: 20px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
            animation: fadeIn 0.5s ease-out forwards;
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useRef, useEffect, useMemo } = React;

        // --- Icons ---
        const IconBase = ({ children, size = 24, className = "" }) => (
            <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
                {children}
            </svg>
        );

        const Umbrella = (props) => <IconBase {...props}><path d="M22 12a10.06 10.06 1 0 0-20 0Z"/><path d="M12 12v8a2 2 0 0 0 4 0"/><path d="M12 2v1"/></IconBase>;
        const Sun = (props) => <IconBase {...props}><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></IconBase>;
        const Calendar = (props) => <IconBase {...props}><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></IconBase>;
        const DollarSign = (props) => <IconBase {...props}><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></IconBase>;
        const TrendingUp = (props) => <IconBase {...props}><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></IconBase>;
        const AlertTriangle = (props) => <IconBase {...props}><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></IconBase>;
        const CheckCircle = (props) => <IconBase {...props}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></IconBase>;
        const Menu = (props) => <IconBase {...props}><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></IconBase>;
        const X = (props) => <IconBase {...props}><path d="M18 6 6 18"/><path d="m6 6 12 12"/></IconBase>;
        const Search = (props) => <IconBase {...props}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></IconBase>;
        const Download = (props) => <IconBase {...props}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></IconBase>;
        const Printer = (props) => <IconBase {...props}><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></IconBase>;
        const Users = (props) => <IconBase {...props}><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></IconBase>;
        const Briefcase = (props) => <IconBase {...props}><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></IconBase>;
        const ChevronRight = (props) => <IconBase {...props}><path d="m9 18 6-6-6-6"/></IconBase>;
        const FileSpreadsheet = (props) => <IconBase {...props}><path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"/><path d="M14 2v6h6"/><path d="M8 12h8"/><path d="M8 16h8"/><path d="M8 20h8"/></IconBase>;
        const UploadCloud = (props) => <IconBase {...props}><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></IconBase>;
        const Target = (props) => <IconBase {...props}><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></IconBase>;
        const RefreshCw = (props) => <IconBase {...props}><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></IconBase>;
        const Lock = (props) => <IconBase {...props}><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></IconBase>;

        // --- CONSTANTS ---
        const AVG_DAILY_WAGE = 100000; 
        const EXCLUDED_DEPTS = ['성남공장', '델리하임', '기타', '대상델리하임'];

        // --- Initial Mock Data ---
        const initialMonthlyTrend = [
            { month: '1월', rate: 15, liability: 1.24 },
            { month: '2월', rate: 20, liability: 1.20 },
            { month: '3월', rate: 18, liability: 1.18 },
            { month: '4월', rate: 25, liability: 1.15 },
            { month: '5월', rate: 35, liability: 1.10 },
            { month: '6월', rate: 40, liability: 1.05 },
        ];

        const initialDeptData = [
            { name: 'R&D센터', usageRate: 18, liability: 380000000, employees: 45, avgRemaining: 14.8, status: 'Critical' },
            { name: '생산본부', usageRate: 32, liability: 450000000, employees: 80, avgRemaining: 12.5, status: 'Warning' },
            { name: '국내영업팀', usageRate: 48, liability: 150000000, employees: 25, avgRemaining: 8.1, status: 'Normal' },
            { name: '마케팅본부', usageRate: 65, liability: 120000000, employees: 18, avgRemaining: 5.2, status: 'Good' },
            { name: '경영지원팀', usageRate: 72, liability: 85000000, employees: 12, avgRemaining: 4.5, status: 'Good' },
        ];

        const initialRiskData = [
            { name: '김철수', dept: 'R&D S/W', used: 2, remaining: 23, reason: '잔여 20일 이상' },
            { name: '이영희', dept: '해외영업', used: 3.5, remaining: 18, reason: '잔여 15일 이상' },
            { name: '박준형', dept: '생산관리', used: 4, remaining: 16, reason: '잔여 15일 이상' },
            { name: '최민수', dept: '생산본부', used: 1, remaining: 25, reason: '잔여 25일 이상' },
            { name: '정수민', dept: '경영지원팀', used: 5, remaining: 15, reason: '잔여 15일 이상' },
        ];

        const initialPromotionEvents = [
            { date: '2/14 (금)', name: '샌드위치 데이', impact: 'High', savings: '₩1,500만' },
            { date: '2/28 (금)', name: '전사 리프레시 데이', impact: 'Medium', savings: '₩800만' },
            { date: '3/10 (월)', name: '창립기념일 대체휴무', impact: 'High', savings: '₩1,200만' },
        ];

        // --- Logic: Data Processing ---
        const processRawData = (rawData) => {
            const deptMap = {};
            const riskList = [];
            const monthSums = Array(12).fill(0);
            let totalEntitlement = 0;

            rawData.forEach(row => {
                const deptName = row['소속'] || '기타';
                
                if (EXCLUDED_DEPTS.includes(deptName)) return;

                const totalDays = Number(row['합계']) || 0;
                const usedDays = Number(row['사용일수']) || 0;
                const remainingDays = Number(row['잔여일수']) || 0;
                const name = row['성명'];
                
                const liabilityBudget = Number(row['부채예산']) || 0;
                const liabilityBalance = Number(row['부채잔액']) || (remainingDays * AVG_DAILY_WAGE);

                if (!deptMap[deptName]) {
                    deptMap[deptName] = { 
                        name: deptName, 
                        totalDays: 0, 
                        usedDays: 0, 
                        remainingDays: 0, 
                        employees: 0,
                        liability: 0
                    };
                }
                deptMap[deptName].totalDays += totalDays;
                deptMap[deptName].usedDays += usedDays;
                deptMap[deptName].remainingDays += remainingDays;
                deptMap[deptName].employees += 1;
                deptMap[deptName].liability += liabilityBalance;

                if (remainingDays >= 10) {
                    riskList.push({
                        name: name,
                        dept: deptName,
                        used: usedDays,
                        remaining: remainingDays,
                        reason: `잔여 ${remainingDays}일`
                    });
                }

                totalEntitlement += totalDays;
                for (let i = 1; i <= 12; i++) {
                    const monthKey = `${i}월`;
                    const val = Number(row[monthKey]) || 0;
                    monthSums[i-1] += val;
                }
            });

            let processedDeptData = Object.values(deptMap).map(d => {
                const usageRate = d.totalDays > 0 ? ((d.usedDays / d.totalDays) * 100).toFixed(1) : 0;
                const avgRemaining = d.employees > 0 ? (d.remainingDays / d.employees).toFixed(1) : 0;
                
                let status = 'Good';
                if (usageRate < 30) status = 'Critical';
                else if (usageRate < 50) status = 'Warning';
                else if (usageRate < 70) status = 'Normal';

                return {
                    name: d.name,
                    usageRate: usageRate,
                    liability: d.liability,
                    employees: d.employees,
                    avgRemaining: avgRemaining,
                    status: status
                };
            });

            processedDeptData.sort((a, b) => Number(a.usageRate) - Number(b.usageRate));

            const processedTrendData = monthSums.map((sum, idx) => {
                const rate = totalEntitlement > 0 ? ((sum / totalEntitlement) * 100).toFixed(1) : 0;
                const estimated = 1.5 - (idx * 0.05); 
                return {
                    month: `${idx + 1}월`,
                    rate: rate,
                    liability: Math.max(0, estimated).toFixed(2)
                };
            });

            return {
                deptData: processedDeptData,
                riskData: riskList.sort((a,b) => b.remaining - a.remaining),
                trendData: processedTrendData
            };
        };

        const calculateKPIs = (deptData, riskData) => {
            const totalLiability = deptData.reduce((acc, curr) => acc + (Number(curr.liability) || 0), 0);
            const totalEmployees = deptData.reduce((acc, curr) => acc + (Number(curr.employees) || 0), 0);
            
            let weightedRateSum = 0;
            let weightedRemSum = 0;

            deptData.forEach(d => {
                weightedRateSum += (Number(d.usageRate) * d.employees);
                weightedRemSum += (Number(d.avgRemaining) * d.employees);
            });

            const avgUsageRate = totalEmployees > 0 ? (weightedRateSum / totalEmployees).toFixed(1) : 0;
            const totalAvgRemaining = totalEmployees > 0 ? (weightedRemSum / totalEmployees).toFixed(1) : 0;
            const liabilityInEok = (totalLiability / 100000000).toFixed(2); 

            return [
                { title: "전사 연차 소진율", value: `${avgUsageRate}%`, sub: "목표 60% 대비 Gap", status: avgUsageRate < 50 ? "Warning" : "Good", icon: Umbrella, color: "bg-blue-50 text-blue-600" },
                { title: "미사용 연차 부채", value: `₩${liabilityInEok}억`, sub: "전체 미사용 수당 합계", status: "Critical", icon: DollarSign, color: "bg-rose-50 text-rose-600" },
                { title: "사용 촉진 대상자", value: `${riskData.length}명`, sub: "집중 관리 대상 (잔여 과다)", status: "Warning", icon: Users, color: "bg-amber-50 text-amber-600" },
                { title: "인당 평균 잔여일", value: `${totalAvgRemaining}일`, sub: "회계연도 마감 2개월 전", status: "Normal", icon: Calendar, color: "bg-emerald-50 text-emerald-600" },
            ];
        };

        // --- Excel Utilities ---
        const exportToExcel = (deptData, riskData, trendData, promoData) => {
            const wb = XLSX.utils.book_new();
            
            const rawExample = [
                {
                    "소속": "QA팀", "사번": "230021", "성명": "홍길동", "자격등급": "L3", 
                    "확정년차22": 15, "확정근속31": 0, "쿼터차이": 0, "임시년차": 0, "기초년차": 15, "근속년차": 0,
                    "합계": 15, "잔여일수": 6, "사용일수": 9, "신청일수": 0, "사용차이": 0,
                    "1월": 1, "2월": 0.5, "3월": 0.5, "4월": 0, "5월": 0, "6월": 0.5,
                    "7월": 3, "8월": 1, "9월": 0.5, "10월": 1.5, "11월": 0, "12월": 0.5,
                    "그룹입사일": "2023-01-02", "회사입사일": "2023-01-02",
                    "부채예산": 1500000, "부채잔액": 600000 
                }
            ];
            const wsRaw = XLSX.utils.json_to_sheet(rawExample);
            XLSX.utils.book_append_sheet(wb, wsRaw, "원천데이터");

            const promoKorean = promoData.map(p => ({
                "날짜": p.date,
                "이벤트명": p.name,
                "절감효과": p.savings
            }));
            const wsPromo = XLSX.utils.json_to_sheet(promoKorean);
            XLSX.utils.book_append_sheet(wb, wsPromo, "촉진일정");

            const deptKorean = deptData.map(d => ({
                "부서명": d.name,
                "소진율": d.usageRate,
                "인원": d.employees,
                "평균잔여일": d.avgRemaining,
                "상태": d.status,
                "예상부채": d.liability
            }));
            const wsDept = XLSX.utils.json_to_sheet(deptKorean);
            XLSX.utils.book_append_sheet(wb, wsDept, "부서현황");

            XLSX.writeFile(wb, "연차관리_통합템플릿.xlsx");
        };

        const readExcel = (file, callback) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                const result = {};

                if (workbook.Sheets["원천데이터"]) {
                    const rawJson = XLSX.utils.sheet_to_json(workbook.Sheets["원천데이터"]);
                    const processed = processRawData(rawJson);
                    result.deptData = processed.deptData;
                    result.riskData = processed.riskData;
                    result.trendData = processed.trendData;
                }

                if (workbook.Sheets["촉진일정"]) {
                    const promoJson = XLSX.utils.sheet_to_json(workbook.Sheets["촉진일정"]);
                    result.promoData = promoJson.map(p => ({
                        date: p["날짜"] || p.date,
                        name: p["이벤트명"] || p.name,
                        savings: p["절감효과"] || p.savings
                    }));
                }

                callback(result);
            };
            reader.readAsArrayBuffer(file);
        };

        // --- Password Modal Component ---
        const PasswordModal = ({ onVerify, onClose }) => {
            const [input, setInput] = useState('');
            const [error, setError] = useState(false);

            const handleSubmit = (e) => {
                e.preventDefault();
                if (input === '1550') {
                    onVerify();
                } else {
                    setError(true);
                    setInput('');
                }
            };

            return (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn">
                    <div className="bg-white rounded-2xl p-8 w-80 shadow-2xl">
                        <div className="flex justify-center mb-4">
                            <div className="p-3 bg-indigo-100 rounded-full text-indigo-600">
                                <Lock size={32} />
                            </div>
                        </div>
                        <h3 className="text-xl font-bold text-center text-slate-800 mb-2">관리자 인증</h3>
                        <p className="text-xs text-center text-slate-500 mb-6">데이터 접근을 위해 비밀번호를 입력하세요.</p>
                        
                        <form onSubmit={handleSubmit}>
                            <input 
                                type="password" 
                                className={`w-full px-4 py-2 border rounded-lg text-center font-bold tracking-widest mb-4 focus:outline-none focus:ring-2 ${error ? 'border-rose-500 focus:ring-rose-200' : 'border-slate-200 focus:ring-indigo-200'}`}
                                placeholder="●●●●"
                                value={input}
                                onChange={(e) => { setInput(e.target.value); setError(false); }}
                                autoFocus
                            />
                            {error && <p className="text-xs text-rose-500 text-center mb-4">비밀번호가 일치하지 않습니다.</p>}
                            <div className="flex gap-2">
                                <button 
                                    type="button" 
                                    onClick={onClose}
                                    className="flex-1 py-2 bg-slate-100 text-slate-600 rounded-lg text-sm font-bold hover:bg-slate-200 transition-colors"
                                >
                                    취소
                                </button>
                                <button 
                                    type="submit" 
                                    className="flex-1 py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-colors shadow-md"
                                >
                                    확인
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            );
        };

        // --- Components ---
        const KPICard = ({ item }) => (
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-start justify-between hover:shadow-md transition-shadow">
                <div>
                    <p className="text-slate-500 text-sm font-medium mb-1">{item.title}</p>
                    <h3 className="text-2xl font-bold text-slate-800 mb-1">{item.value}</h3>
                    <p className={`text-xs font-medium ${
                        item.status === 'Good' ? 'text-emerald-600' :
                        item.status === 'Warning' ? 'text-amber-600' : 
                        item.status === 'Critical' ? 'text-rose-600' : 'text-slate-500'
                    }`}>
                        {item.sub}
                    </p>
                </div>
                <div className={`p-3 rounded-xl ${item.color}`}>
                    <item.icon size={24} />
                </div>
            </div>
        );

        const TotalUsageBar = ({ kpi }) => {
            const rate = parseFloat(kpi.value) || 0;
            
            return (
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm mt-6">
                    <div className="flex justify-between items-end mb-2">
                        <div>
                            <h3 className="text-lg font-bold text-slate-800">전사 연차 소진율 현황</h3>
                            <p className="text-sm text-slate-500">전체 임직원 평균 소진율</p>
                        </div>
                        <span className={`text-2xl font-bold ${
                            rate < 50 ? 'text-rose-600' : 
                            rate < 70 ? 'text-amber-500' : 'text-emerald-600'
                        }`}>{rate}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden relative">
                        <div className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10" style={{ left: '60%' }} title="목표 60%"></div>
                        <div 
                            className={`h-full rounded-full transition-all duration-1000 ${
                                rate < 50 ? 'bg-rose-500' : 
                                rate < 70 ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${Math.min(rate, 100)}%` }}
                        ></div>
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 mt-2">
                        <span>0%</span>
                        <span className="font-bold text-slate-600">목표 60%</span>
                        <span>100%</span>
                    </div>
                </div>
            );
        };

        const TrendChart = ({ data, maxRate }) => {
            const maxLiability = Math.max(...data.map(d => parseFloat(d.liability || 0)), 1.5) * 1.2; 
            
            const height = 200; 
            const width = 600;  
            const padding = 40;
            const barWidth = 30;

            const getRateY = (rate) => {
                const clampedRate = Math.min(rate, maxRate);
                return height - (clampedRate / maxRate) * height;
            };
            
            const step = (width - padding * 2) / (data.length - 1 || 1);

            const points = data.map((d, i) => {
                const x = padding + i * step;
                const y = getRateY(parseFloat(d.rate || 0));
                return `${x},${y}`;
            }).join(' ');

            return (
                <div className="w-full h-72 relative">
                    <div className="absolute left-0 top-0 bottom-8 flex flex-col justify-between text-xs text-blue-500 font-bold">
                        <span>{maxRate}%</span>
                        <span>{Math.round(maxRate/2)}%</span>
                        <span>0%</span>
                    </div>
                    <div className="absolute right-0 top-0 bottom-8 flex flex-col justify-between text-xs text-rose-500 font-bold text-right">
                        <span>{maxLiability.toFixed(1)}억</span>
                        <span>{(maxLiability/2).toFixed(1)}억</span>
                        <span>0억</span>
                    </div>

                    <div className="absolute inset-0 left-8 right-8 bottom-6">
                        <svg viewBox={`0 0 ${width} ${height + 20}`} className="w-full h-full overflow-visible">
                            <line x1="0" y1="0" x2={width} y2="0" stroke="#f1f5f9" strokeWidth="1" />
                            <line x1="0" y1={height/2} x2={width} y2={height/2} stroke="#f1f5f9" strokeWidth="1" />
                            <line x1="0" y1={height} x2={width} y2={height} stroke="#e2e8f0" strokeWidth="1" />

                            {data.map((d, i) => {
                                const x = padding + i * step;
                                const barH = (parseFloat(d.liability || 0) / maxLiability) * height;
                                return (
                                    <g key={`bar-${i}`} className="group">
                                        <rect 
                                            x={x - barWidth/2} 
                                            y={height - barH} 
                                            width={barWidth} 
                                            height={barH} 
                                            fill="#f43f5e" 
                                            className="opacity-20 group-hover:opacity-40 transition-opacity cursor-pointer"
                                            rx="4"
                                        />
                                        <text x={x} y={height - barH - 5} textAnchor="middle" fontSize="10" fill="#f43f5e" className="opacity-0 group-hover:opacity-100 font-bold">
                                            {d.liability}억
                                        </text>
                                    </g>
                                );
                            })}

                            <polyline 
                                fill="none" 
                                stroke="#3b82f6" 
                                strokeWidth="3" 
                                points={points} 
                                strokeLinecap="round" 
                                strokeLinejoin="round"
                            />

                            {data.map((d, i) => {
                                const x = padding + i * step;
                                const y = getRateY(parseFloat(d.rate || 0));
                                return (
                                    <g key={`point-${i}`} className="group">
                                        <circle cx={x} cy={y} r="5" fill="white" stroke="#3b82f6" strokeWidth="3" className="cursor-pointer hover:r-7 transition-all"/>
                                        <text x={x} y={y - 10} textAnchor="middle" fontSize="12" fill="#3b82f6" className="opacity-0 group-hover:opacity-100 font-bold">
                                            {d.rate}%
                                        </text>
                                        <text x={x} y={height + 20} textAnchor="middle" fontSize="12" fill="#64748b" fontWeight="bold">
                                            {d.month}
                                        </text>
                                    </g>
                                );
                            })}
                        </svg>
                    </div>
                    
                    <div className="absolute top-0 right-10 flex gap-4 text-xs bg-white/80 p-2 rounded-lg border border-slate-100">
                        <span className="flex items-center gap-1"><div className="w-3 h-1 bg-blue-500 rounded-full"></div>연차 소진율(%)</span>
                        <span className="flex items-center gap-1"><div className="w-3 h-3 bg-rose-500 opacity-30 rounded-sm"></div>부채 잔액(억원)</span>
                    </div>
                </div>
            );
        };

        const DeptProgress = ({ data, onDeptClick, selectedDept }) => {
            return (
                <div className="space-y-3">
                    {data.map((d, i) => (
                        <div 
                            key={i} 
                            onClick={() => onDeptClick(d.name)}
                            className={`group p-3 rounded-lg transition-all cursor-pointer border ${
                                selectedDept === d.name 
                                    ? 'bg-indigo-50 border-indigo-300 ring-1 ring-indigo-200 shadow-sm' 
                                    : 'hover:bg-slate-50 border-transparent hover:border-slate-200'
                            }`}
                        >
                            <div className="flex justify-between text-sm mb-2">
                                <span className={`font-bold ${selectedDept === d.name ? 'text-indigo-800' : 'text-slate-700'}`}>
                                    {d.name}
                                </span>
                                <span className="text-slate-500">
                                    <span className={`font-bold ${
                                        d.status === 'Critical' ? 'text-rose-600' : 
                                        d.status === 'Warning' ? 'text-amber-600' : 'text-emerald-600'
                                    }`}>{d.usageRate}%</span> 소진
                                </span>
                            </div>
                            <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                                <div 
                                    className={`h-full rounded-full transition-all duration-500 ${
                                        d.status === 'Critical' ? 'bg-rose-500' : 
                                        d.status === 'Warning' ? 'bg-amber-500' : 'bg-emerald-500'
                                    }`}
                                    style={{ width: `${Math.min(d.usageRate, 100)}%` }}
                                ></div>
                            </div>
                            <div className="flex justify-between mt-2 text-[11px] text-slate-500">
                                <span>인원: {d.employees}명</span>
                                <span>부채: ₩{(d.liability/100000000).toFixed(1)}억</span>
                            </div>
                        </div>
                    ))}
                </div>
            );
        };

        // --- Excel Data View Component ---
        const ExcelDataManager = ({ deptData, riskData, trendData, promoData, onUpload, onDownload }) => {
            const fileInputRef = useRef(null);

            const handleFileChange = (e) => {
                const file = e.target.files[0];
                if (!file) return;
                onUpload(file);
                e.target.value = null; 
            };

            return (
                <div className="space-y-8 animate-fadeIn">
                    <div className="bg-gradient-to-r from-emerald-50 to-teal-50 p-6 rounded-2xl border border-emerald-100 flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-white text-emerald-600 rounded-xl shadow-sm border border-emerald-100">
                                <FileSpreadsheet size={32} />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-slate-800">통합 데이터 관리 센터</h3>
                                <p className="text-sm text-slate-600">제공된 양식에 원본 데이터를 붙여넣어 업로드하세요.</p>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <button 
                                onClick={onDownload}
                                className="flex items-center gap-2 px-5 py-3 bg-white border border-emerald-200 text-emerald-700 text-sm font-bold rounded-xl hover:bg-emerald-50 transition-colors shadow-sm"
                            >
                                <Download size={18} /> 통합 템플릿 다운로드 (.xlsx)
                            </button>
                            <button 
                                onClick={() => fileInputRef.current.click()}
                                className="flex items-center gap-2 px-5 py-3 bg-emerald-600 text-white text-sm font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-200"
                            >
                                <UploadCloud size={18} /> 통합 데이터 업로드
                            </button>
                            <input 
                                type="file" 
                                ref={fileInputRef} 
                                className="hidden" 
                                accept=".xlsx, .xls" 
                                onChange={handleFileChange}
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-2 mb-4">
                                <h3 className="text-lg font-bold text-slate-800">분석 결과: 부서별 현황</h3>
                                <span className="text-xs bg-emerald-100 text-emerald-600 px-2 py-1 rounded">대시보드 자동 연동</span>
                            </div>
                            <div className="overflow-x-auto border rounded-lg border-slate-200 max-h-64 custom-scrollbar">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 sticky top-0">
                                        <tr>
                                            <th className="px-4 py-3">부서명</th>
                                            <th className="px-4 py-3 text-center">소진율</th>
                                            <th className="px-4 py-3 text-center">인원</th>
                                            <th className="px-4 py-3 text-right">예상부채</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {deptData.map((row, i) => (
                                            <tr key={i} className="hover:bg-slate-50">
                                                <td className="px-4 py-3 font-medium text-slate-700">{row.name}</td>
                                                <td className="px-4 py-3 text-center">{row.usageRate}%</td>
                                                <td className="px-4 py-3 text-center">{row.employees}</td>
                                                <td className="px-4 py-3 text-right font-mono text-rose-600">{row.liability?.toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <div className="flex items-center gap-2 mb-4">
                                <h3 className="text-lg font-bold text-slate-800">촉진 일정 (Editable)</h3>
                                <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded">사용자 입력</span>
                            </div>
                            <div className="overflow-x-auto border rounded-lg border-slate-200 max-h-64 custom-scrollbar">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 sticky top-0">
                                        <tr>
                                            <th className="px-4 py-3">날짜</th>
                                            <th className="px-4 py-3">이벤트명</th>
                                            <th className="px-4 py-3">절감효과</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {promoData.map((row, i) => (
                                            <tr key={i} className="hover:bg-slate-50">
                                                <td className="px-4 py-3 text-slate-500">{row.date}</td>
                                                <td className="px-4 py-3 font-medium text-slate-700">{row.name}</td>
                                                <td className="px-4 py-3 text-emerald-600">{row.savings}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        const App = () => {
            const [isSidebarOpen, setIsSidebarOpen] = useState(false);
            const [activeTab, setActiveTab] = useState('Dashboard');
            
            const [deptData, setDeptData] = useState(initialDeptData);
            const [riskData, setRiskData] = useState(initialRiskData);
            const [trendData, setTrendData] = useState(initialMonthlyTrend);
            const [promoData, setPromoData] = useState(initialPromotionEvents);
            
            const [selectedDept, setSelectedDept] = useState('All');
            const [filterDept, setFilterDept] = useState('All');
            const [filterDays, setFilterDays] = useState('15'); 
            const [trendScale, setTrendScale] = useState(100); 
            
            const [isVerified, setIsVerified] = useState(false);
            const [showPasswordModal, setShowPasswordModal] = useState(false);

            const kpis = useMemo(() => calculateKPIs(deptData, riskData), [deptData, riskData]);

            const handleDeptClick = (deptName) => {
                if (selectedDept === deptName) {
                    setSelectedDept('All');
                    setFilterDept('All'); 
                } else {
                    setSelectedDept(deptName);
                    setFilterDept(deptName); 
                }
            };

            const filteredRiskData = riskData.filter(item => {
                const deptMatch = filterDept === 'All' || item.dept === filterDept;
                const daysLimit = parseInt(filterDays);
                const daysMatch = item.remaining >= daysLimit;
                return deptMatch && daysMatch;
            });

            const uniqueDepts = ['All', ...new Set(riskData.map(r => r.dept))];

            const handleTabChange = (tabName) => {
                if (tabName === 'Excel' && !isVerified) {
                    setShowPasswordModal(true);
                } else {
                    setActiveTab(tabName);
                }
            };

            const handlePasswordSuccess = () => {
                setIsVerified(true);
                setShowPasswordModal(false);
                setActiveTab('Excel');
            };

            const handleUpload = (file) => {
                readExcel(file, (result) => {
                    if (result.deptData && result.deptData.length > 0) setDeptData(result.deptData);
                    if (result.riskData && result.riskData.length > 0) setRiskData(result.riskData);
                    if (result.trendData && result.trendData.length > 0) setTrendData(result.trendData);
                    if (result.promoData && result.promoData.length > 0) setPromoData(result.promoData);
                    alert("데이터가 성공적으로 업데이트되었습니다!");
                });
            };

            const handleDownload = () => {
                exportToExcel(deptData, riskData, trendData, promoData);
            };

            return (
                <div className="flex h-screen bg-slate-50 text-slate-800 font-sans overflow-hidden">
                    {showPasswordModal && (
                        <PasswordModal 
                            onVerify={handlePasswordSuccess} 
                            onClose={() => setShowPasswordModal(false)} 
                        />
                    )}

                    <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 transform transition-transform duration-300 lg:relative lg:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                        <div className="flex items-center gap-3 p-6 h-20 border-b border-slate-100">
                            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">HR</div>
                            <span className="font-bold text-lg text-slate-800">연차 관리 센터</span>
                            <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden ml-auto text-slate-400">
                                <X size={24} />
                            </button>
                        </div>
                        <nav className="p-4 space-y-1">
                            <div className="px-4 py-2 text-xs font-semibold text-slate-400 uppercase">Dashboard</div>
                            <button 
                                onClick={() => handleTabChange('Dashboard')}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium border-l-4 transition-colors ${
                                    activeTab === 'Dashboard' 
                                        ? 'bg-indigo-50 text-indigo-700 border-indigo-600' 
                                        : 'text-slate-500 hover:bg-slate-50 border-transparent'
                                }`}
                            >
                                <Sun size={20} /> 연차 촉진 대시보드
                            </button>
                            <div className="px-4 py-2 mt-4 text-xs font-semibold text-slate-400 uppercase">Data Management</div>
                            <button 
                                onClick={() => handleTabChange('Excel')}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium border-l-4 transition-colors ${
                                    activeTab === 'Excel' 
                                        ? 'bg-emerald-50 text-emerald-700 border-emerald-600' 
                                        : 'text-slate-500 hover:bg-slate-50 border-transparent'
                                }`}
                            >
                                <FileSpreadsheet size={20} /> 데이터 관리 (Excel)
                            </button>
                        </nav>
                    </aside>

                    <main className="flex-1 flex flex-col h-full overflow-hidden">
                        <header className="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-10 shrink-0">
                            <div className="flex items-center gap-4">
                                <button onClick={() => setIsSidebarOpen(true)} className="lg:hidden p-2 text-slate-600">
                                    <Menu size={24} />
                                </button>
                                <div>
                                    <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                                        {activeTab === 'Dashboard' ? '연차 사용 현황 및 부채 관리' : '연차 데이터 통합 관리'}
                                        <span className="text-xs font-medium bg-indigo-50 text-indigo-600 px-2 py-1 rounded border border-indigo-100">FY 2026</span>
                                    </h1>
                                    <p className="text-xs text-slate-500 mt-0.5">최종 업데이트: 경영지원팀</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                {activeTab === 'Excel' && (
                                    <div className="text-xs text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full font-bold flex items-center gap-2">
                                        <RefreshCw size={12} /> 데이터 연동 준비 완료
                                    </div>
                                )}
                                <div className="flex items-center gap-2">
                                    <button className="p-2 text-slate-400 hover:bg-slate-100 rounded-full transition-colors"><Printer size={20} /></button>
                                </div>
                            </div>
                        </header>

                        <div className="flex-1 overflow-auto p-8 bg-slate-50/50">
                            <div className="max-w-7xl mx-auto space-y-10">
                                {activeTab === 'Dashboard' ? (
                                    <>
                                        <section>
                                            <div className="flex items-center gap-3 mb-6">
                                                <div className="p-2.5 bg-blue-100 text-blue-600 rounded-xl shadow-sm"><DollarSign size={24} /></div>
                                                <div>
                                                    <h2 className="text-xl font-bold text-slate-800">1. 재무 영향도 및 전사 현황</h2>
                                                    <p className="text-sm text-slate-500">연차 소진율과 부채(비용)의 상관관계를 분석합니다.</p>
                                                </div>
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                                                {kpis.map((kpi, idx) => (
                                                    <KPICard key={idx} item={kpi} />
                                                ))}
                                            </div>
                                            
                                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                                <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                                                    <div className="flex justify-between items-center mb-6">
                                                        <h3 className="text-lg font-bold text-slate-800">월별 연차 소진율 및 부채 추이</h3>
                                                        <div className="flex gap-2 items-center">
                                                            <span className="text-xs text-slate-500">소진율 기준:</span>
                                                            <select 
                                                                className="text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-600 focus:outline-none focus:border-indigo-500"
                                                                value={trendScale}
                                                                onChange={(e) => setTrendScale(Number(e.target.value))}
                                                            >
                                                                <option value={100}>100%</option>
                                                                <option value={50}>50%</option>
                                                                <option value={30}>30%</option>
                                                            </select>
                                                        </div>
                                                    </div>
                                                    <TrendChart data={trendData} maxRate={trendScale} />
                                                    <div className="mt-6 p-4 bg-indigo-50 rounded-xl border border-indigo-100 flex items-start gap-3">
                                                        <div className="p-2 bg-white rounded-full text-indigo-600 shadow-sm"><TrendingUp size={16} /></div>
                                                        <div>
                                                            <h4 className="font-bold text-indigo-900 text-sm">Financial Insight</h4>
                                                            <p className="text-xs text-indigo-700 leading-relaxed mt-1">
                                                                현재 추세라면 회계연도 말 예상 미사용 수당은 <strong>약 {(kpis[1].value)}</strong>입니다. 
                                                                목표 소진율 달성 시 상당한 비용 절감이 예상됩니다.
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                                <div className="lg:col-span-1 h-full">
                                                    <TotalUsageBar kpi={kpis[0]} />
                                                </div>
                                            </div>
                                        </section>

                                        <section>
                                            <div className="flex items-center gap-3 mb-6">
                                                <div className="p-2.5 bg-rose-100 text-rose-600 rounded-xl shadow-sm"><AlertTriangle size={24} /></div>
                                                <div>
                                                    <h2 className="text-xl font-bold text-slate-800">2. 부서별 휴식 현황과 케어 필요 인원</h2>
                                                    <p className="text-sm text-slate-500">부서별 연차 사용 흐름을 파악하고, 휴식이 부족한 동료를 미리 챙겨주세요.</p>
                                                </div>
                                            </div>
                                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col h-full">
                                                    <div className="flex justify-between items-center mb-6">
                                                        <h3 className="text-lg font-bold text-slate-800">부서별 소진율 현황 (Click to Filter)</h3>
                                                        <button 
                                                            className="text-xs bg-slate-100 px-2 py-1 rounded text-slate-500"
                                                            onClick={() => { setSelectedDept('All'); setFilterDept('All'); }}
                                                        >
                                                            전체 보기
                                                        </button>
                                                    </div>
                                                    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                                                        <DeptProgress 
                                                            data={deptData} 
                                                            onDeptClick={handleDeptClick} 
                                                            selectedDept={selectedDept} 
                                                        />
                                                    </div>
                                                    <div className="mt-6 pt-4 border-t border-slate-100">
                                                        <div className="flex items-center gap-2 p-3 bg-rose-50 rounded-lg border border-rose-100">
                                                            <AlertTriangle size={16} className="text-rose-500 shrink-0" />
                                                            <p className="text-xs text-rose-700"><strong>소진율 저조 부서</strong>에 대한 적극적인 독려가 필요합니다.</p>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-full flex flex-col">
                                                    <div className="flex flex-col gap-4 mb-4">
                                                        <div className="flex justify-between items-center">
                                                            <h3 className="text-lg font-bold text-slate-800">휴식 권장 대상 (Care Group)</h3>
                                                            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded">
                                                                {filteredRiskData.length}명
                                                            </span>
                                                        </div>
                                                        
                                                        <div className="flex gap-2">
                                                            <select 
                                                                className="text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-600 focus:outline-none focus:border-indigo-500"
                                                                value={filterDept}
                                                                onChange={(e) => {
                                                                    setFilterDept(e.target.value);
                                                                    setSelectedDept(e.target.value); 
                                                                }}
                                                            >
                                                                <option value="All">전체 부서</option>
                                                                {uniqueDepts.filter(d => d !== 'All').map(d => (
                                                                    <option key={d} value={d}>{d}</option>
                                                                ))}
                                                            </select>
                                                            <select 
                                                                className="text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-600 focus:outline-none focus:border-indigo-500"
                                                                value={filterDays}
                                                                onChange={(e) => setFilterDays(e.target.value)}
                                                            >
                                                                <option value="10">잔여 10일 이상</option>
                                                                <option value="15">잔여 15일 이상</option>
                                                                <option value="20">잔여 20일 이상</option>
                                                                <option value="25">잔여 25일 이상</option>
                                                            </select>
                                                        </div>
                                                    </div>

                                                    <div className="overflow-x-auto flex-1 custom-scrollbar max-h-[300px]">
                                                        <table className="w-full text-left text-sm">
                                                            <thead className="bg-slate-50 text-slate-500 sticky top-0">
                                                                <tr>
                                                                    <th className="px-4 py-2 rounded-l-lg">성명/직급</th>
                                                                    <th className="px-4 py-2">소속</th>
                                                                    <th className="px-4 py-2 text-center">잔여일수</th>
                                                                    <th className="px-4 py-2 rounded-r-lg">비고</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-slate-50">
                                                                {filteredRiskData.length > 0 ? (
                                                                    filteredRiskData.map((emp, i) => (
                                                                        <tr key={i} className="hover:bg-slate-50">
                                                                            <td className="px-4 py-3 font-bold text-slate-700">{emp.name}</td>
                                                                            <td className="px-4 py-3 text-slate-500">{emp.dept}</td>
                                                                            <td className="px-4 py-3 text-center">
                                                                                <span className="px-2 py-1 bg-rose-100 text-rose-600 rounded font-bold text-xs">
                                                                                    {emp.remaining}일
                                                                                </span>
                                                                            </td>
                                                                            <td className="px-4 py-3 text-slate-500 text-xs">{emp.reason}</td>
                                                                        </tr>
                                                                    ))
                                                                ) : (
                                                                    <tr>
                                                                        <td colSpan="4" className="text-center py-8 text-slate-400 text-sm">
                                                                            해당 조건의 대상자가 없습니다.
                                                                        </td>
                                                                    </tr>
                                                                )}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                    
                                                    {filteredRiskData.length > 0 && (
                                                        <button className="w-full mt-4 py-3 text-sm text-indigo-600 font-medium bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors flex items-center justify-center gap-2">
                                                            <Users size={16} /> 대상자({filteredRiskData.length}명) 독려 메일 발송
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </section>

                                        <section>
                                            <div className="flex items-center gap-3 mb-6">
                                                <div className="p-2.5 bg-emerald-100 text-emerald-600 rounded-xl shadow-sm"><Target size={24} /></div>
                                                <div>
                                                    <h2 className="text-xl font-bold text-slate-800">3. 촉진 전략 및 실행 가이드</h2>
                                                    <p className="text-sm text-slate-500">비용 절감과 리프레시를 위한 구체적인 실행 계획입니다.</p>
                                                </div>
                                            </div>
                                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                                                    <div className="flex justify-between items-center mb-4">
                                                        <h3 className="text-lg font-bold text-slate-800">연차 촉진 권장일 (Golden Days)</h3>
                                                        <span className="text-xs px-2 py-1 bg-emerald-50 text-emerald-600 rounded font-bold border border-emerald-100">Cost Saving Plan</span>
                                                    </div>
                                                    <div className="space-y-3">
                                                        {promoData.map((evt, i) => (
                                                            <div key={i} className="flex items-center p-3 border border-slate-100 rounded-xl hover:border-indigo-200 transition-colors bg-slate-50/50">
                                                                <div className="w-12 h-12 bg-white rounded-lg flex flex-col items-center justify-center border border-slate-100 shadow-sm shrink-0">
                                                                    <span className="text-[10px] text-slate-400 font-bold uppercase">{evt.date.split('(')[0].split('/')[0]}월</span>
                                                                    <span className="text-sm font-bold text-slate-800">{evt.date.split('(')[0].split('/')[1]}</span>
                                                                </div>
                                                                <div className="ml-4 flex-1">
                                                                    <div className="flex justify-between">
                                                                        <h4 className="font-bold text-slate-700">{evt.name}</h4>
                                                                        <span className="text-xs font-bold text-emerald-600">절감예상 {evt.savings}</span>
                                                                    </div>
                                                                    <div className="flex items-center gap-2 mt-1">
                                                                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                                                                            evt.impact === 'High' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-200 text-slate-600'
                                                                        }`}>효과: {evt.impact}</span>
                                                                        <span className="text-xs text-slate-400">{evt.date}</span>
                                                                    </div>
                                                                </div>
                                                                <button className="ml-2 p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"><CheckCircle size={18} /></button>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-6 rounded-2xl text-white flex flex-col justify-between relative overflow-hidden">
                                                    <div className="absolute top-0 right-0 -mr-10 -mt-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>
                                                    <div>
                                                        <h3 className="text-lg font-bold mb-1">부서장 Action Guide</h3>
                                                        <p className="text-indigo-100 text-sm mb-6">연차 사용은 직원의 '권리'이자 회사의 '비용 절감' 전략입니다. 아래 내용을 팀 미팅 시 공유해주세요.</p>
                                                        <ul className="space-y-3">
                                                            <li className="flex items-center gap-3 bg-white/10 p-3 rounded-lg backdrop-blur-sm"><CheckCircle size={18} className="text-emerald-300 shrink-0" /><span className="text-sm font-medium">샌드위치 데이(2/14) 팀 전원 휴무 권장</span></li>
                                                            <li className="flex items-center gap-3 bg-white/10 p-3 rounded-lg backdrop-blur-sm"><CheckCircle size={18} className="text-emerald-300 shrink-0" /><span className="text-sm font-medium">잔여 연차 10일 이상자 휴가 계획서 징구</span></li>
                                                            <li className="flex items-center gap-3 bg-white/10 p-3 rounded-lg backdrop-blur-sm"><CheckCircle size={18} className="text-emerald-300 shrink-0" /><span className="text-sm font-medium">업무 대행자 지정 및 인수인계 파일 점검</span></li>
                                                        </ul>
                                                    </div>
                                                    <button className="w-full mt-6 py-3 bg-white text-indigo-600 font-bold rounded-xl shadow-lg hover:bg-indigo-50 transition-colors">가이드라인 공지 발송</button>
                                                </div>
                                            </div>
                                        </section>
                                    </>
                                ) : (
                                    <ExcelDataManager 
                                        deptData={deptData} 
                                        riskData={riskData} 
                                        trendData={trendData}
                                        promoData={promoData}
                                        onUpload={handleUpload}
                                        onDownload={handleDownload}
                                    />
                                )}
                            </div>
                        </div>
                    </main>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
