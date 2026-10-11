import { Table, Button, Space } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import type { ColumnsType, TableProps } from "antd/es/table";

interface DataTableProps<T extends object> {
    rows?: T[];
    columns: ColumnsType<T>;
    isLoading?: boolean;
    onAddClick?: () => void;
    addButtonLabel?: string;
    rowKey?: TableProps<T>["rowKey"];
    onRowClick?: (record: T) => void;
}

const DataTable = <T extends object>({
    rows = [],
    columns,
    isLoading,
    onAddClick,
    addButtonLabel = "Добавить",
    rowKey = "id",
    onRowClick,
}: DataTableProps<T>) => {
    return (
        <Space orientation="vertical" size={12} style={{ width: "100%" }}>
            {onAddClick && (
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                    <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={onAddClick}
                    >
                        {addButtonLabel}
                    </Button>
                </div>
            )}
            <Table
                dataSource={rows}
                columns={columns}
                loading={isLoading}
                rowKey={rowKey}
                bordered={false}
                onRow={(record) => ({
                    onClick: () => onRowClick && onRowClick(record),
                    style: onRowClick ? { cursor: 'pointer' } : undefined,
                })}
                pagination={{ pageSize: 10, showSizeChanger: true, pageSizeOptions: [10, 25, 50] }}
                style={{ borderRadius: 12, overflow: "hidden" }}
                scroll={{ x: "max-content" }}
                locale={{ emptyText: "Нет данных" }}
            />
        </Space>
    );
};

export default DataTable;
