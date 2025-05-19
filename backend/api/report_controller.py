#!/usr/bin/env python3
# SecureScout - Report Controller API

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file

# Initialize Blueprint
report_bp = Blueprint('report', __name__)
logger = logging.getLogger(__name__)

@report_bp.route('/generate/<scan_id>', methods=['POST'])
def generate_report(scan_id):
    """
    Generate a security report for a completed scan
    """
    # Check if scan exists in active_scans (imported from scan_controller)
    from api.scan_controller import active_scans
    
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan_info = active_scans[scan_id]
    
    # Check if scan is complete
    if scan_info['status'] not in ['completed', 'stopped']:
        return jsonify({'error': 'Cannot generate report for an incomplete scan'}), 400
    
    try:
        # Create report filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        report_filename = f"securescout_report_{scan_id}_{timestamp}.json"
        report_path = os.path.join(current_app.config['REPORTS_DIR'], report_filename)
        
        # Ensure reports directory exists
        os.makedirs(current_app.config['REPORTS_DIR'], exist_ok=True)
        
        # Generate report data
        report_data = {
            'report_id': f"report_{scan_id}_{timestamp}",
            'scan_id': scan_id,
            'target_url': scan_info['target_url'],
            'scan_type': scan_info['scan_type'],
            'scan_modules': scan_info['modules'],
            'start_time': scan_info['start_time'],
            'end_time': datetime.utcnow().isoformat(),
            'duration': get_elapsed_time(scan_info['start_time']),
            'findings': scan_info['findings'],
            'summary': generate_findings_summary(scan_info['findings']),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Write report to file
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Report generated for scan {scan_id}: {report_path}")
        
        return jsonify({
            'status': 'success',
            'message': 'Report generated successfully',
            'report_id': report_data['report_id'],
            'report_path': report_path
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@report_bp.route('/list', methods=['GET'])
def list_reports():
    """
    List all available reports
    """
    try:
        reports_dir = current_app.config['REPORTS_DIR']
        
        # Ensure directory exists
        os.makedirs(reports_dir, exist_ok=True)
        
        # Get all report files
        report_files = [f for f in os.listdir(reports_dir) if f.startswith('securescout_report_')]
        
        reports = []
        for filename in report_files:
            report_path = os.path.join(reports_dir, filename)
            
            # Extract scan_id from filename
            parts = filename.split('_')
            if len(parts) >= 3:
                scan_id = parts[2]
            else:
                scan_id = "unknown"
            
            # Get file stats
            stats = os.stat(report_path)
            
            reports.append({
                'filename': filename,
                'path': report_path,
                'scan_id': scan_id,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
            })
        
        return jsonify({
            'status': 'success',
            'reports': reports
        })
        
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        return jsonify({'error': str(e)}), 500


@report_bp.route('/download/<filename>', methods=['GET'])
def download_report(filename):
    """
    Download a specific report file
    """
    try:
        report_path = os.path.join(current_app.config['REPORTS_DIR'], filename)
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        return send_file(report_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@report_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_report(filename):
    """
    Delete a specific report file
    """
    try:
        report_path = os.path.join(current_app.config['REPORTS_DIR'], filename)
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        os.remove(report_path)
        
        return jsonify({
            'status': 'success',
            'message': f'Report {filename} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        return jsonify({'error': str(e)}), 500


def get_elapsed_time(start_time_iso):
    """Calculate elapsed time from ISO format start time to now"""
    start_time = datetime.fromisoformat(start_time_iso)
    elapsed = datetime.utcnow() - start_time
    return str(elapsed).split('.')[0]  # Remove microseconds


def generate_findings_summary(findings):
    """Generate a summary of findings by severity and category"""
    severity_counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'info': 0
    }
    
    category_counts = {}
    
    for finding in findings:
        # Count by severity
        severity = finding.get('severity', 'info').lower()
        if severity in severity_counts:
            severity_counts[severity] += 1
        else:
            severity_counts['info'] += 1
        
        # Count by category
        category = finding.get('category', 'Other')
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1
    
    return {
        'total_findings': len(findings),
        'by_severity': severity_counts,
        'by_category': category_counts
    }