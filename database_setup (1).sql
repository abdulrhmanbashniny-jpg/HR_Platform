-- ====================================
-- منصة إدارة الموارد البشرية
-- ملف إنشاء قاعدة البيانات
-- ====================================

-- جدول الموظفين
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    hire_date DATE,
    salary DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- جدول الطلبات
CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    emp_id TEXT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    emp_name TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    details TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT DEFAULT 'معلق' CHECK (status IN ('معلق', 'موافق عليه', 'مرفوض')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    approved_by TEXT,
    approved_at TIMESTAMP,
    rejection_reason TEXT
);

-- جدول الجوازات
CREATE TABLE IF NOT EXISTS passports (
    id SERIAL PRIMARY KEY,
    emp_id TEXT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    passport_number TEXT UNIQUE NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    nationality TEXT NOT NULL,
    place_of_issue TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- جدول الإقامات
CREATE TABLE IF NOT EXISTS residencies (
    id SERIAL PRIMARY KEY,
    emp_id TEXT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    residency_number TEXT UNIQUE NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    sponsor TEXT,
    profession TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- جدول سجل النشاط
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    emp_id TEXT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول التنبيهات
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    emp_id TEXT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info' CHECK (type IN ('info', 'warning', 'error', 'success')),
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- إنشاء فهارس لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_requests_emp_id ON requests(emp_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_created_at ON requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_passports_emp_id ON passports(emp_id);
CREATE INDEX IF NOT EXISTS idx_passports_expiry ON passports(expiry_date);
CREATE INDEX IF NOT EXISTS idx_residencies_emp_id ON residencies(emp_id);
CREATE INDEX IF NOT EXISTS idx_residencies_expiry ON residencies(expiry_date);
CREATE INDEX IF NOT EXISTS idx_activity_emp_id ON activity_log(emp_id);
CREATE INDEX IF NOT EXISTS idx_notifications_emp_id ON notifications(emp_id);

-- إدراج بيانات تجريبية للموظفين
INSERT INTO employees (id, name, role, department, email, hire_date, salary) VALUES
('001', 'أحمد محمد', 'موظف عادي', 'تقنية المعلومات', 'ahmed@company.com', '2020-01-15', 8000.00),
('002', 'فاطمة أحمد', 'محاسبة', 'المحاسبة', 'fatima@company.com', '2019-05-20', 9000.00),
('003', 'محمود خالد', 'مدير المبيعات', 'المبيعات', 'mahmoud@company.com', '2018-03-10', 12000.00),
('004', 'نور حسين', 'منسقة إدارية', 'الإدارة العامة', 'noor@company.com', '2021-07-01', 7000.00),
('005', 'سارة علي', 'مديرة النظام', 'الموارد البشرية', 'sarah@company.com', '2017-02-14', 15000.00)
ON CONFLICT (id) DO NOTHING;

-- إدراج بيانات تجريبية للطلبات
INSERT INTO requests (id, emp_id, emp_name, type, title, details, start_date, end_date, status) VALUES
('REQ-20251130001', '001', 'أحمد محمد', 'إجازة', 'طلب إجازة سنوية', 'إجازة لمدة أسبوع', '2025-12-15', '2025-12-22', 'معلق'),
('REQ-20251130002', '002', 'فاطمة أحمد', 'سلفة', 'طلب سلفة راتب', 'سلفة بمبلغ 3000 ريال', '2025-12-01', '2025-12-01', 'موافق عليه'),
('REQ-20251130003', '003', 'محمود خالد', 'رحلة عمل', 'رحلة عمل خارجية', 'زيارة عميل في دبي', '2025-12-10', '2025-12-12', 'معلق')
ON CONFLICT (id) DO NOTHING;

-- دالة لتحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- تطبيق الدالة على الجداول
DROP TRIGGER IF EXISTS update_employees_updated_at ON employees;
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_requests_updated_at ON requests;
CREATE TRIGGER update_requests_updated_at BEFORE UPDATE ON requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_passports_updated_at ON passports;
CREATE TRIGGER update_passports_updated_at BEFORE UPDATE ON passports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_residencies_updated_at ON residencies;
CREATE TRIGGER update_residencies_updated_at BEFORE UPDATE ON residencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- دالة للتحقق من انتهاء صلاحية الوثائق
CREATE OR REPLACE FUNCTION check_document_expiry()
RETURNS TABLE(
    doc_type TEXT,
    emp_id TEXT,
    emp_name TEXT,
    doc_number TEXT,
    expiry_date DATE,
    days_remaining INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'جواز سفر'::TEXT,
        p.emp_id,
        e.name,
        p.passport_number,
        p.expiry_date,
        (p.expiry_date - CURRENT_DATE)::INTEGER
    FROM passports p
    JOIN employees e ON p.emp_id = e.id
    WHERE p.expiry_date <= CURRENT_DATE + INTERVAL '90 days'
    AND p.expiry_date >= CURRENT_DATE
    
    UNION ALL
    
    SELECT 
        'إقامة'::TEXT,
        r.emp_id,
        e.name,
        r.residency_number,
        r.expiry_date,
        (r.expiry_date - CURRENT_DATE)::INTEGER
    FROM residencies r
    JOIN employees e ON r.emp_id = e.id
    WHERE r.expiry_date <= CURRENT_DATE + INTERVAL '90 days'
    AND r.expiry_date >= CURRENT_DATE
    
    ORDER BY expiry_date;
END;
$$ LANGUAGE plpgsql;

-- عرض إحصائيات سريعة
CREATE OR REPLACE VIEW stats_summary AS
SELECT 
    (SELECT COUNT(*) FROM employees WHERE is_active = true) as active_employees,
    (SELECT COUNT(*) FROM requests WHERE status = 'معلق') as pending_requests,
    (SELECT COUNT(*) FROM passports WHERE expiry_date <= CURRENT_DATE + INTERVAL '90 days') as expiring_passports,
    (SELECT COUNT(*) FROM residencies WHERE expiry_date <= CURRENT_DATE + INTERVAL '90 days') as expiring_residencies;

-- تعليقات على الجداول
COMMENT ON TABLE employees IS 'جدول بيانات الموظفين';
COMMENT ON TABLE requests IS 'جدول طلبات الموظفين';
COMMENT ON TABLE passports IS 'جدول بيانات جوازات السفر';
COMMENT ON TABLE residencies IS 'جدول بيانات الإقامات';
COMMENT ON TABLE activity_log IS 'سجل نشاط المستخدمين';
COMMENT ON TABLE notifications IS 'جدول التنبيهات';
