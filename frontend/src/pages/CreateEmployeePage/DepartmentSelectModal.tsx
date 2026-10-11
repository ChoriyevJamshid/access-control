import { useState } from 'react';
import { Modal, Table, Input } from 'antd';
import { useQuery } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import { getDepartments } from '@/entities/enterprise/api/enterpriseApi';
import type { Department } from '@/entities/employee/types';

interface DepartmentSelectModalProps {
    open: boolean;
    onClose: () => void;
    onSelect: (departmentId: number) => void;
}

const columns: ColumnsType<Department> = [
    {
        title: 'ID',
        dataIndex: 'id',
        key: 'id',
        width: 80,
    },
    {
        title: 'Название',
        dataIndex: 'name',
        key: 'name',
    },
    {
        title: 'Код',
        dataIndex: 'code',
        key: 'code',
    },
];

const DepartmentSelectModal = ({ open, onClose, onSelect }: DepartmentSelectModalProps) => {
    const [searchText, setSearchText] = useState('');

    const { data: departments, isLoading } = useQuery({
        queryKey: ['departments'],
        queryFn: getDepartments,
        enabled: open,
    });

    const filteredDepartments = departments?.filter((dept) =>
        dept.name.toLowerCase().includes(searchText.toLowerCase()) ||
        dept.code.toLowerCase().includes(searchText.toLowerCase()) ||
        String(dept.id).includes(searchText)
    );

    return (
        <Modal
            title="Выберите отдел"
            open={open}
            onCancel={onClose}
            footer={null}
            width={700}
        >
            <Input.Search
                placeholder="Поиск по названию, коду или ID..."
                allowClear
                onChange={(e) => setSearchText(e.target.value)}
                style={{ marginBottom: 16 }}
            />
            <Table
                columns={columns}
                dataSource={filteredDepartments}
                rowKey="id"
                loading={isLoading}
                onRow={(record) => ({
                    onClick: () => {
                        onSelect(record.id);
                    },
                    style: { cursor: 'pointer' },
                })}
                pagination={{ pageSize: 10 }}
                size="middle"
                scroll={{ y: 400 }}
            />
        </Modal>
    );
};

export default DepartmentSelectModal;
